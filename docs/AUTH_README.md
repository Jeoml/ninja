# Authentication System

A complete email-based OTP authentication system with JWT tokens for the Quiz application.

## Features

- 📧 **Email OTP Verification**: Send 6-digit OTP codes via email
- 🔐 **JWT Authentication**: Secure token-based authentication
- 🗄️ **Database Integration**: PostgreSQL with user and OTP management
- ⏰ **Automatic Expiry**: OTPs expire after 5 minutes
- 🔒 **Security**: Secure password hashing and token validation
- 📱 **Modern API**: RESTful API with FastAPI

## Flow

1. **Send OTP**: User provides email → System sends OTP via email
2. **Verify OTP**: User enters OTP → System verifies and creates/updates user
3. **Get Token**: Upon successful verification → System returns JWT token
4. **Authenticated Requests**: Use JWT token for protected endpoints

## API Endpoints

### Public Endpoints
- `POST /auth/send-otp` - Send OTP to email
- `POST /auth/verify-otp` - Verify OTP and get JWT token

### Protected Endpoints (Require JWT Token)
- `GET /auth/me` - Get current user info
- `POST /auth/refresh-token` - Refresh JWT token

### Utility Endpoints
- `GET /` - API information
- `GET /health` - Health check

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### OTPs Table
```sql
CREATE TABLE otps (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0
);
```

## Configuration

The system uses environment variables for configuration. Key settings:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT signing
- `SMTP_*` - Email service configuration
- `OTP_EXPIRE_MINUTES` - OTP expiry time (default: 5 minutes)

## Email Service

Supports SMTP email sending with:
- HTML and plain text email templates
- Professional OTP email design
- Configurable SMTP settings
- Connection testing

## Security Features

- JWT tokens with configurable expiry
- OTP rate limiting and attempt tracking
- Secure password handling
- Database connection pooling
- Input validation with Pydantic
- CORS configuration

## Module Structure

```
auth/
├── __init__.py          # Package initialization
├── config.py            # Configuration settings
├── database.py          # Database models and operations
├── email_service.py     # Email sending service
├── jwt_service.py       # JWT token operations
├── models.py            # Pydantic models
├── otp_service.py       # OTP generation and verification
└── README.md            # This file
```
