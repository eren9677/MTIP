import bcrypt
import sqlite3
from database import create_connection

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def register_user(username, password):
    """Register a new user"""
    conn = create_connection()
    if conn is None:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if cursor.fetchone() is not None:
            conn.close()
            return False, "Username already exists"
        
        # Hash password and insert new user
        hashed = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, hashed_password) VALUES (?, ?)',
            (username, hashed)
        )
        conn.commit()
        return True, "Registration successful"
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def verify_login(username, password):
    """Verify user login credentials"""
    conn = create_connection()
    if conn is None:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT user_id, hashed_password FROM users WHERE username = ?',
            (username,)
        )
        user_data = cursor.fetchone()
        
        if user_data is None:
            return False, "Invalid username or password"
        
        user_id, stored_hash = user_data
        
        if verify_password(password, stored_hash):
            return True, user_id
        return False, "Invalid username or password"
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()