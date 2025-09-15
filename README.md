# Quiz Auth System

A comprehensive quiz platform with email-based authentication and AI-powered adaptive learning.

## 🚀 Features

### 🔐 Authentication System
- **Email OTP Verification**: Secure login with 6-digit codes sent via email
- **JWT Tokens**: Stateless authentication for API access
- **User Management**: PostgreSQL-backed user profiles and sessions

### 🤖 AI Agents - Round 1 Quiz
- **Adaptive Questions**: Intelligently selects questions from different topics
- **Performance Tracking**: Real-time catalog of user strengths and weaknesses
- **Smart Logic**: Topics with mixed results are marked as "solved"
- **Diverse Coverage**: 131+ questions across 9+ Excel topics

## 📁 Project Structure

```
ninja_assignment/
├── main.py                    # FastAPI application entry point
├── requirements.txt           # All dependencies
├── data.csv                   # Quiz questions database
│
├── auth/                      # Authentication module
│   ├── config.py             # Configuration settings
│   ├── database.py           # Database utilities
│   ├── email_service.py      # OTP email sending
│   ├── jwt_service.py        # JWT token management
│   ├── otp_service.py        # OTP generation/verification
│   └── models.py             # Pydantic models
│
├── ai_agents/                 # AI Agents package
│   └── round1/               # Round 1 quiz system
│       ├── api.py            # FastAPI routes
│       ├── quiz_service.py   # Quiz orchestration
│       ├── catalog_service.py # Performance tracking
│       ├── database_service.py # Question fetching
│       └── models.py         # API models
│
├── scripts/                   # Utility scripts
│   ├── insert_quiz_data.py   # Database setup script
│   ├── run_tests.py          # Test runner
│   └── simulate_round1.py    # Full quiz simulation
│
├── tests/                     # Test suite
│   ├── simple_test.py        # Basic functionality tests
│   ├── test_imports.py       # Import validation
│   ├── test_database_service.py # Database tests
│   ├── test_quiz_service.py  # Quiz logic tests
│   └── test_api_endpoints.py # API endpoint tests
│
└── docs/                      # Documentation
    ├── AUTH_README.md         # Authentication system docs
    ├── ROUND1_README.md       # Round 1 quiz docs
    └── ARCHITECTURE_REVIEW.md # Architecture analysis
```

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python scripts/insert_quiz_data.py
```

### 3. Configure Email (Optional)
Update `auth/config.py` with your Gmail SMTP credentials for OTP functionality.

### 4. Run Application
```bash
python main.py
```

Server will start at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Interactive Docs**: `http://localhost:8000/docs`
- **API Schema**: `http://localhost:8000/openapi.json`

### Key Endpoints

#### Authentication
- `POST /auth/send-otp` - Send OTP to email
- `POST /auth/verify-otp` - Verify OTP and get JWT token
- `GET /auth/me` - Get current user info (requires JWT)

#### Round 1 Quiz (No Auth Required)
- `GET /ai-agents/round1/chat/intro` - Get started
- `POST /ai-agents/round1/start` - Start quiz session
- `GET /ai-agents/round1/question` - Get next question
- `POST /ai-agents/round1/answer` - Submit answer (A/B/C/D)
- `GET /ai-agents/round1/performance` - View performance catalog

## 🧪 Testing

### Run All Tests
```bash
python scripts/run_tests.py
```

### Run Simple Tests
```bash
python tests/simple_test.py
```

### Simulate Full Quiz
```bash
python scripts/simulate_round1.py
```

## 🎯 Round 1 Quiz Flow

1. **Start Session**: Configure number of questions (default: 15)
2. **Answer Questions**: Multiple choice (A/B/C/D) from diverse topics
3. **Real-time Feedback**: Immediate correct/incorrect responses
4. **Performance Tracking**: Live catalog of topic mastery
5. **Final Results**: Comprehensive strengths/weaknesses analysis

### Topic Catalog Logic
- ✅ **Solved**: Only correct answers OR mixed correct/incorrect
- ❌ **Unsolved**: Only incorrect answers
- 📊 **Smart Selection**: Prioritizes unexplored topics

## 🔧 Configuration

### Database
- PostgreSQL connection via `auth/config.py`
- Shared connection utilities across modules
- Automatic table creation

### Email Service
- Gmail SMTP support
- HTML email templates
- Configurable OTP settings

### JWT Tokens
- HS256 algorithm
- Configurable expiration
- Secure secret key management

## 📖 Documentation

- **[Authentication System](docs/AUTH_README.md)** - Detailed auth flow
- **[Round 1 Quiz](docs/ROUND1_README.md)** - Quiz system architecture  
- **[Architecture Review](docs/ARCHITECTURE_REVIEW.md)** - Technical analysis

## 🚀 Future Enhancements

- Additional quiz rounds with difficulty progression
- Persistent user sessions and progress tracking
- Advanced analytics and reporting
- Multiplayer quiz competitions
- Mobile app integration

## 🤝 Development

### Project Principles
- **Single Source of Truth**: Centralized configuration
- **Code Reuse**: Shared utilities across modules
- **Clean Architecture**: Separated concerns and dependencies
- **Comprehensive Testing**: Multiple test layers
- **Clear Documentation**: Self-documenting code and APIs

---

**Built with FastAPI, PostgreSQL, and modern Python practices** 🐍