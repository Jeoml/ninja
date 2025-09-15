# Backend Service

Authentication and Agent Helper APIs for the Quiz System.

## Features

- **Authentication System**: OTP-based email authentication with JWT tokens
- **Quiz APIs**: Round 1 and Round 2 quiz systems
- **Agent Helper**: Question retrieval and response recording
- **Database Integration**: PostgreSQL with response tracking

## Environment Variables

Set these in Railway:

```
DATABASE_URL=postgresql://...
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
JWT_SECRET_KEY=your-jwt-secret
```

## API Endpoints

- `POST /auth/send-otp` - Send OTP to email
- `POST /auth/verify-otp` - Verify OTP and get JWT token
- `GET /auth/me` - Get current user info
- `GET /agent-helper/topics` - Get all topics
- `GET /agent-helper/get-question` - Get question by topic/difficulty
- `POST /agent-helper/record-response` - Record user response
- `GET /agent-helper/session-responses` - Get session responses
- `GET /agent-helper/session-performance` - Get session performance

## Deployment

Deploy to Railway:
1. Connect this folder as a Railway service
2. Set environment variables
3. Deploy
