import sys
import bcrypt
import psycopg2

def create_user(email, password):
    # Hash the password
    hash_val = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        dbname="demoDB",
        user="postgres",
        password="Rainbow@87909"
    )
    cur = conn.cursor()
    
    try:
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
            (email, hash_val)
        )
        conn.commit()
        print(f"User created: {email}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 create_user.py <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    create_user(email, password)
