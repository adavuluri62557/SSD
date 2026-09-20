import os
import sys
import bcrypt
import psycopg2

def _get_env(*names, default=None):
	for name in names:
		value = os.getenv(name)
		if value not in (None, ""):
			return value
	return default

def create_user(name, email, password):
	password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()

	conn = psycopg2.connect(
		host=_get_env("DB_HOST", default="localhost"),
		dbname=_get_env("DB_NAME", "DB_DATABASE", default="demoDB"),
		user=_get_env("DB_USER", "DB_USERNAME", default="postgres"),
		password=_get_env("DB_PASS", "DB_PASSWORD", default="Rainbow@87909"),
		port=_get_env("DB_PORT", default="5432"),
	)
	cur = conn.cursor()

	try:
		try:
			cur.execute(
				"INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
				(name, email, password_hash),
			)
		except psycopg2.errors.UndefinedColumn:
			cur.execute(
				"INSERT INTO users (email, password_hash) VALUES (%s, %s)",
				(email, password_hash),
			)
		conn.commit()
		print(f"User created: {email}")
	except Exception as e:
		conn.rollback()
		print(f"Error: {e}")
	finally:
		cur.close()
		conn.close()

if __name__ == "__main__":
	if len(sys.argv) not in (4, 3):
		print("Usage: python3 create_user2.py <name> <email> <password>")
		sys.exit(1)

	name = sys.argv[1]
	email = sys.argv[2]
	password = sys.argv[3] if len(sys.argv) == 4 else None
	if password is None:
		print("Password is required.")
		sys.exit(1)

	create_user(name, email, password)
