# Application Layer Security - Beginner Guide
import hashlib
import secrets
import re
import html
# 1. Validate Username (Input Validation)
#--------------------------------------------------
def validate_username(username):
    """Check if username is valid"""
    # Username: 3-20 characters, letters/numbers/underscore only
    pattern = r"^[A-Za-z0-9_]{3,20}$"
    return re.match(pattern, username) is not None
# 2. Hash Password Securely
#--------------------------------------------------
def hash_password(password):
    """Create a secure password hash"""
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt, password_hash
# 3. Verify Password
#--------------------------------------------------
def verify_password(password, salt, stored_hash):
    """Check if password is correct"""
    new_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return secrets.compare_digest(new_hash, stored_hash)
# 4. Prevent SQL Injection
#--------------------------------------------------
def prevent_sql_injection(user_input):
    """Remove dangerous SQL characters"""
    dangerous = ["'", '"', ";", "--"]
    for char in dangerous:
        user_input = user_input.replace(char, "")
    return user_input
# 5. Prevent XSS (Cross-Site Scripting)
#--------------------------------------------------
def prevent_xss(user_input):
    """Convert HTML special characters"""
    return html.escape(user_input)
# Get username and password from user
username = input("Enter username: ")
password = input("Enter password: ")
print("\n--- APPLICATION LAYER SECURITY CHECK ---\n")
# Step 1: Validate username
if not validate_username(username):
    print("Invalid username!")
    print("   (Must be 3-20 characters, letters/numbers/_)")
else:
    print("✓ Username is valid")
    # Step 2: Prevent SQL Injection
    clean_username = prevent_sql_injection(username)
    print("✓ SQL injection prevention applied")
    # Step 3: Hash and verify password
    salt, password_hash = hash_password(password)
    if verify_password(password, salt, password_hash):
        print("✓ Password is correct")
        print("\n--- SECURITY FEATURES DEMONSTRATED ---\n")
        # Show XSS Prevention
        print("1. XSS Prevention (HTML Escaping):")
        dangerous_text = "<script>alert('XSS')</script>"
        safe_text = prevent_xss(dangerous_text)
        print(f"   Before: {dangerous_text}")
        print(f"   After:  {safe_text}\n")
        # Show SQL Injection Prevention
        print("2. SQL Injection Prevention:")
        bad_input = "admin'; DROP TABLE users;--"
        good_input = prevent_sql_injection(bad_input)
        print(f"   Before: {bad_input}")
        print(f"   After:  {good_input}\n")
        print("Login successful!")
    else:
        print("Password is incorrect")