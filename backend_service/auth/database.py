"""
Database connection and models for authentication system.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from .config import DATABASE_URL

def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@contextmanager
def get_db():
    """Context manager for database connections."""
    connection = None
    try:
        connection = get_db_connection()
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

def create_auth_tables():
    """Create authentication tables if they don't exist."""
    
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        is_verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    );
    """
    
    create_otps_table = """
    CREATE TABLE IF NOT EXISTS otps (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        otp_code VARCHAR(10) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        is_used BOOLEAN DEFAULT FALSE,
        attempts INTEGER DEFAULT 0
    );
    """
    
    create_index_email = """
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_otps_email ON otps(email);
    CREATE INDEX IF NOT EXISTS idx_otps_expires_at ON otps(expires_at);
    """
    
    with get_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(create_users_table)
            cursor.execute(create_otps_table)
            cursor.execute(create_index_email)
            connection.commit()
            print("✅ Authentication tables created successfully")

class UserDB:
    """User database operations."""
    
    @staticmethod
    def create_user(email: str):
        """Create a new user or return existing user."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                # Check if user exists
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user:
                    return dict(user)
                
                # Create new user
                cursor.execute(
                    "INSERT INTO users (email) VALUES (%s) RETURNING *",
                    (email,)
                )
                connection.commit()
                return dict(cursor.fetchone())
    
    @staticmethod
    def get_user_by_email(email: str):
        """Get user by email."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                return dict(user) if user else None
    
    @staticmethod
    def verify_user(email: str):
        """Mark user as verified."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET is_verified = TRUE WHERE email = %s",
                    (email,)
                )
                connection.commit()
    
    @staticmethod
    def update_last_login(email: str):
        """Update user's last login timestamp."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE email = %s",
                    (email,)
                )
                connection.commit()

class OTPDB:
    """OTP database operations."""
    
    @staticmethod
    def create_otp(email: str, otp_code: str, expires_at):
        """Create a new OTP."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                # Invalidate previous OTPs for this email
                cursor.execute(
                    "UPDATE otps SET is_used = TRUE WHERE email = %s AND is_used = FALSE",
                    (email,)
                )
                
                # Create new OTP
                cursor.execute(
                    "INSERT INTO otps (email, otp_code, expires_at) VALUES (%s, %s, %s) RETURNING *",
                    (email, otp_code, expires_at)
                )
                connection.commit()
                return dict(cursor.fetchone())
    
    @staticmethod
    def verify_otp(email: str, otp_code: str):
        """Verify OTP and mark as used."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                # Get valid OTP
                cursor.execute("""
                    SELECT * FROM otps 
                    WHERE email = %s AND otp_code = %s AND is_used = FALSE 
                    AND expires_at > CURRENT_TIMESTAMP
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (email, otp_code))
                
                otp = cursor.fetchone()
                
                if otp:
                    # Mark OTP as used
                    cursor.execute(
                        "UPDATE otps SET is_used = TRUE WHERE id = %s",
                        (otp['id'],)
                    )
                    connection.commit()
                    return True
                
                # Increment attempts for invalid OTP
                cursor.execute(
                    "UPDATE otps SET attempts = attempts + 1 WHERE email = %s AND is_used = FALSE",
                    (email,)
                )
                connection.commit()
                return False
    
    @staticmethod
    def cleanup_expired_otps():
        """Clean up expired OTPs."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM otps WHERE expires_at < CURRENT_TIMESTAMP")
                connection.commit()
