"""
Configuration settings for the authentication system.
"""
import os
from decouple import config

# Database Configuration
DATABASE_URL = config(
    "DATABASE_URL", 
    default="postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

# JWT Configuration
JWT_SECRET_KEY = config("JWT_SECRET_KEY", default="your-super-secret-jwt-key-change-this-in-production")
JWT_ALGORITHM = config("JWT_ALGORITHM", default="HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)

# Email Configuration
SMTP_SERVER = config("SMTP_SERVER", default="smtp.gmail.com")
SMTP_PORT = config("SMTP_PORT", default=587, cast=int)
SMTP_USERNAME = config("SMTP_USERNAME", default="joel.t.workspace@gmail.com")
SMTP_PASSWORD = config("SMTP_PASSWORD", default="etkyxjpkbmywdjnb")  # App password without spaces
FROM_EMAIL = config("FROM_EMAIL", default="joel.t.workspace@gmail.com")

# OTP Configuration
OTP_EXPIRE_MINUTES = config("OTP_EXPIRE_MINUTES", default=5, cast=int)
OTP_LENGTH = config("OTP_LENGTH", default=6, cast=int)

# Application Configuration
APP_NAME = config("APP_NAME", default="Quiz Auth System")
DEBUG = config("DEBUG", default=True, cast=bool)
