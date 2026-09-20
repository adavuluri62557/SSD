import os
import sys
import subprocess
import importlib
import logging
from contextlib import contextmanager

REQUIRED_PKGS = [
	("psycopg2", "psycopg2-binary"),
	("flask", "flask"),
	("flask_talisman", "flask-talisman"),
	("bcrypt", "bcrypt"),
]

def _print_install_hint(mod, err):
	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)
	logger.error("Missing required module %s: %s", mod, err)
	print(
		f"Missing required Python package for module '{mod}'.\n\n"
		f"Python executable: {sys.executable}\n"
		f"Python version: {sys.version.split()[0]}\n\n"
		f"Install into this Python environment with:\n"
		f"  {sys.executable} -m pip install {next(p for m, p in REQUIRED_PKGS if m == mod)}\n"
	)
	print("sys.path:")
	for p in sys.path:
		print("  " + p)

for mod, pip_name in REQUIRED_PKGS:
	try:
		importlib.import_module(mod)
	except Exception as e:
		if os.getenv("NO_AUTO_INSTALL", "0") in ("1", "true", "True"):
			_print_install_hint(mod, e)
			raise SystemExit(1)
		print(f"Module '{mod}' missing; attempting to install '{pip_name}' into this Python environment...")
		proc = subprocess.run(
			[sys.executable, "-m", "pip", "install", "--upgrade", pip_name],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
		)
		if proc.returncode != 0:
			print(proc.stdout)
			print(proc.stderr)
			_print_install_hint(mod, "pip install failed")
			raise SystemExit(1)
		try:
			importlib.invalidate_caches()
			importlib.import_module(mod)
		except Exception as e2:
			_print_install_hint(mod, e2)
			raise SystemExit(1)

import psycopg2
from psycopg2 import pool, extras
from flask import Flask, request, jsonify
from flask_talisman import Talisman
import bcrypt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _get_env(*names, default=None):
	for name in names:
		value = os.getenv(name)
		if value not in (None, ""):
			return value
	return default

def load_db_config():
	cfg = {
		"host": _get_env("DB_HOST"),
		"dbname": _get_env("DB_NAME", "DB_DATABASE"),
		"user": _get_env("DB_USER", "DB_USERNAME"),
		"password": _get_env("DB_PASS", "DB_PASSWORD"),
		"port": int(_get_env("DB_PORT", default="5432")) if _get_env("DB_PORT") else None,
		"sslrootcert": _get_env("DB_SSLROOTCERT"),
		"minconn": int(_get_env("DB_MIN_CONN", default="1")),
		"maxconn": int(_get_env("DB_MAX_CONN", default="10")),
	}
	# Only check for required fields (not sslrootcert)
	required = ["host", "dbname", "user", "password"]
	missing = [k for k in required if k not in cfg or cfg[k] in (None, "")]
	if missing:
		logger.error("Missing DB config: %s", missing)
		logger.error(
			"Set DB_HOST, DB_NAME/DB_DATABASE, DB_USER/DB_USERNAME, and DB_PASS/DB_PASSWORD before starting the app."
		)
		raise RuntimeError("Missing DB configuration")
	return cfg

_db_pool = None

def init_db_pool():
	global _db_pool
	if _db_pool:
		return _db_pool
	try:
		cfg = load_db_config()
	except RuntimeError as e:
		logger.warning("DB pool not initialized: %s", e)
		_db_pool = None
		return None

	conn_kwargs = {
		"minconn": cfg["minconn"],
		"maxconn": cfg["maxconn"],
		"host": cfg["host"],
		"dbname": cfg["dbname"],
		"user": cfg["user"],
		"password": cfg["password"],
	}
	if cfg["port"]:
		conn_kwargs["port"] = cfg["port"]

	if cfg["sslrootcert"]:
		conn_kwargs["sslmode"] = "verify-full"
		conn_kwargs["sslrootcert"] = cfg["sslrootcert"]
	else:
		conn_kwargs["sslmode"] = "disable"

	_db_pool = pool.ThreadedConnectionPool(**conn_kwargs)
	return _db_pool

@contextmanager
def db_conn():
	p = init_db_pool()
	if not p:
		raise RuntimeError("Database not configured (missing DB_* environment variables)")
	conn = p.getconn()
	try:
		yield conn
	finally:
		p.putconn(conn)

def execute_query(query, params=None, fetchone=False, fetchall=False):
	with db_conn() as conn:
		try:
			with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
				cur.execute(query, params)
				# Always commit for write queries (INSERT, UPDATE, DELETE)
				if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
					conn.commit()
				if fetchone:
					return cur.fetchone()
				if fetchall:
					return cur.fetchall()
				# Fallback commit for SELECT or other queries
				if not fetchone and not fetchall:
					conn.commit()
		except Exception:
			logger.exception("DB query failed")
			raise

def get_user_by_email(email):
	query = "SELECT id, email, password_hash FROM users WHERE email = %s"
	return execute_query(query, (email,), fetchone=True)

def verify_password(password_plain: str, password_hash: bytes) -> bool:
	try:
		return bcrypt.checkpw(password_plain.encode("utf-8"), password_hash)
	except ValueError:
		return False

app = Flask(__name__)
Talisman(app, force_https=False)

@app.route("/login", methods=["POST"])
def login():
	data = request.get_json() or {}
	email = data.get("email", "").strip()
	password = data.get("password", "")
	if not email or not password:
		return jsonify({"error": "invalid credentials"}), 400

	try:
		row = get_user_by_email(email)
	except RuntimeError as e:
		logger.warning("Login attempted but DB unavailable: %s", e)
		return jsonify({"error": "service unavailable"}), 503
	except Exception:
		return jsonify({"error": "internal error"}), 500

	if not row:
		return jsonify({"error": "invalid credentials"}), 401

	password_hash = row.get("password_hash")
	if isinstance(password_hash, str):
		password_hash = password_hash.encode("utf-8")

	if verify_password(password, password_hash):
		return jsonify({"status": "ok", "user_id": row["id"]}), 200

	return jsonify({"error": "invalid credentials"}), 401

@app.route("/register", methods=["POST"])
def register():
	data = request.get_json() or {}
	email = data.get("email", "").strip()
	password = data.get("password", "")
	if not email or not password:
		return jsonify({"error": "email and password required"}), 400

	# Hash the password
	try:
		password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()
	except Exception:
		return jsonify({"error": "password hashing failed"}), 500

	# Insert into database
	try:
		query = "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id"
		result = execute_query(query, (email, password_hash), fetchone=True)
		if result:
			return jsonify({"status": "registered", "user_id": result["id"]}), 201
	except psycopg2.IntegrityError:
		# Email already exists
		logger.warning("Registration failed: email already exists: %s", email)
		return jsonify({"error": "email already registered"}), 409
	except RuntimeError as e:
		logger.warning("Register attempted but DB unavailable: %s", e)
		return jsonify({"error": "service unavailable"}), 503
	except Exception:
		logger.exception("Registration failed")
		return jsonify({"error": "registration failed"}), 500

	return jsonify({"error": "registration failed"}), 500

if __name__ == "__main__":
	try:
		load_db_config()
	except RuntimeError as e:
		logger.critical("Application startup aborted: %s", e)
		raise SystemExit(1)

	print("Starting app...")
	print("DB_HOST =", os.getenv("DB_HOST"))
	print("DB_NAME =", os.getenv("DB_NAME"))
	print("DB_USER =", os.getenv("DB_USER"))
	print("PORT =", os.getenv("PORT"))
	ssl_cert = os.getenv("WEB_SSL_CERT")
	ssl_key = os.getenv("WEB_SSL_KEY")
	ssl_context = (ssl_cert, ssl_key) if ssl_cert and ssl_key else None

	# Force a clean restart after code changes
	# Ensure the app is started in a fresh terminal window
	app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8443")), ssl_context=ssl_context)