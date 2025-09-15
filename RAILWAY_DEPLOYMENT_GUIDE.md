# Railway Deployment Guide

This project is split into two separate services for Railway deployment:

## 🏗️ Architecture

```
Frontend → Backend Service (Port 8000) → Database
              ↓
          LangGraph Service (Port 8001)
```

## 📦 Service 1: Backend Service

**Location**: `backend_service/` folder

**Contains**:
- Authentication system (auth/)
- Agent helper APIs (agent_helper/) 
- Round 1 & 2 quiz systems (ai_agents/brute/)
- Database operations

**Main file**: `backend_service/main.py`
**Port**: 8000

### Environment Variables for Backend Service:
```
DATABASE_URL=postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
JWT_SECRET_KEY=your-jwt-secret-key
DEBUG=false
```

## 🤖 Service 2: LangGraph Service

**Location**: `langgraph_service/` folder

**Contains**:
- LangGraph agent (langgraph_agent/)
- AI question generation
- User profiling system
- Groq API integration

**Main file**: `langgraph_service/main.py`
**Port**: 8001 (or Railway's assigned PORT)

### Environment Variables for LangGraph Service:
```
BACKEND_SERVICE_URL=https://ninja-production-6ed6.up.railway.app
GROQ_API_KEY=<copy_from_groq_api_key.txt>
DATABASE_URL=postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
PORT=8001
```

**Note**: The Groq API key is stored in `langgraph_service/groq_api_key.txt` - copy this value to the GROQ_API_KEY environment variable in Railway.

## 🚀 Deployment Steps

### Step 1: Deploy Backend Service
1. Create new Railway project for "Backend Service"
2. Connect the `backend_service/` folder
3. Set environment variables listed above
4. Deploy
5. Note the Railway URL (e.g., `https://backend-service-abc123.railway.app`)

### Step 2: Deploy LangGraph Service
1. Create new Railway project for "LangGraph Service"
2. Connect the `langgraph_service/` folder
3. Set environment variables (use Backend Service URL for BACKEND_SERVICE_URL)
4. Deploy
5. Note the Railway URL (e.g., `https://langgraph-service-xyz789.railway.app`)

### Step 3: Update Frontend
Point your frontend to the LangGraph Service URL:
```javascript
const LANGGRAPH_API = "https://langgraph-service-xyz789.railway.app";

// Start assessment
const response = await fetch(`${LANGGRAPH_API}/ai-agents/langgraph/start-quiz`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 'user123' })
});
```

## 🔄 Service Communication

```
Frontend
    ↓
LangGraph Service (Railway #2)
    ↓ HTTP calls
Backend Service (Railway #1)
    ↓
Database
```

The LangGraph Service makes HTTP calls to the Backend Service for:
- Getting topics
- Fetching questions
- Recording responses
- Getting session data

## 📊 API Endpoints

### Backend Service Endpoints:
- `POST /auth/send-otp`
- `POST /auth/verify-otp`
- `GET /auth/me`
- `GET /agent-helper/topics`
- `GET /agent-helper/get-question`
- `POST /agent-helper/record-response`
- `GET /agent-helper/session-responses`
- `GET /agent-helper/session-performance`

### LangGraph Service Endpoints:
- `POST /ai-agents/langgraph/start-quiz`
- `GET /ai-agents/langgraph/user-summary/{session_id}`
- `GET /ai-agents/langgraph/health`
- `GET /ai-agents/langgraph/info`

## 🔧 Local Testing

### Terminal 1 (Backend Service):
```bash
cd backend_service
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

### Terminal 2 (LangGraph Service):
```bash
cd langgraph_service
pip install -r requirements.txt
export BACKEND_SERVICE_URL=http://localhost:8000
python main.py
# Runs on http://localhost:8001
```

### Test Communication:
```bash
# Test backend
curl http://localhost:8000/health

# Test LangGraph
curl http://localhost:8001/health

# Test full workflow
curl -X POST http://localhost:8001/ai-agents/langgraph/start-quiz \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'
```

## 🚨 Important Notes

1. **CORS**: Backend service allows requests from LangGraph service URL
2. **Database**: Both services use the same database but different tables
3. **Security**: Correct answers are never exposed in API responses
4. **Scalability**: Services can be scaled independently
5. **Monitoring**: Each service has its own health check endpoint

## 📝 Files Structure

```
backend_service/
├── main.py                 # Backend FastAPI app
├── requirements.txt        # Backend dependencies
├── railway.json           # Railway config
├── README.md              # Backend documentation
├── auth/                  # Authentication system
├── agent_helper/          # Question and response APIs
└── ai_agents/brute/       # Round 1 & 2 quiz systems

langgraph_service/
├── main.py                # LangGraph FastAPI app
├── requirements.txt       # LangGraph dependencies  
├── railway.json          # Railway config
├── README.md             # LangGraph documentation
└── langgraph_agent/      # AI agent with 6 nodes
```

This setup allows you to deploy and scale each service independently on Railway! 🎯
