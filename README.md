# Ninja Assignment - Railway Deployment Ready

A comprehensive quiz platform split into two independent services for Railway deployment.

## 🏗️ Architecture

This project is split into two microservices:

1. **Backend Service** - Authentication, Questions, Responses
2. **LangGraph Service** - AI-Powered Adaptive Assessments

## 📁 Project Structure

```
ninja_assignment/
├── backend_service/           # 🏗️ Backend Service (Railway #1)
│   ├── main.py               # Backend FastAPI app (Port 8000)
│   ├── requirements.txt      # Backend dependencies
│   ├── railway.json         # Railway deployment config
│   ├── README.md            # Backend service guide
│   ├── auth/                # Authentication system
│   ├── agent_helper/        # Question/Response APIs
│   └── ai_agents/brute/     # Round 1 & 2 quiz systems
│
├── langgraph_service/        # 🤖 LangGraph Service (Railway #2)
│   ├── main.py              # LangGraph FastAPI app (Port 8001)
│   ├── requirements.txt     # AI dependencies (LangGraph, Groq)
│   ├── railway.json        # Railway deployment config
│   ├── README.md           # LangGraph service guide
│   └── langgraph_agent/    # 6-node AI agent system
│
├── data.csv                  # 📊 Quiz questions dataset
├── RAILWAY_DEPLOYMENT_GUIDE.md  # 🚀 Complete deployment guide
└── LANGGRAPH_API_DOCUMENTATION.txt  # 📋 API documentation
```

## 🚀 Quick Start for Railway

### Deploy Backend Service (Service #1):
1. Create new Railway project
2. Connect the `backend_service/` folder
3. Set environment variables (see RAILWAY_DEPLOYMENT_GUIDE.md)
4. Deploy

### Deploy LangGraph Service (Service #2):
1. Create new Railway project  
2. Connect the `langgraph_service/` folder
3. Set BACKEND_SERVICE_URL to your Backend Service Railway URL
4. Set GROQ_API_KEY
5. Deploy

## 🔗 Service Communication

```
Frontend → LangGraph Service → Backend Service → Database
```

- Frontend calls LangGraph Service for AI assessments
- LangGraph Service calls Backend Service for questions/responses
- Backend Service handles all database operations

## 📋 Documentation

- **Deployment Guide**: `RAILWAY_DEPLOYMENT_GUIDE.md`
- **API Documentation**: `LANGGRAPH_API_DOCUMENTATION.txt`
- **Backend Service**: `backend_service/README.md`
- **LangGraph Service**: `langgraph_service/README.md`

## 🎯 Key Features

- ✅ **6-Node AI Workflow**: Adaptive question selection
- ✅ **AI Question Generation**: Self-improving questionnaire
- ✅ **User Profiling**: Comprehensive psychological analysis
- ✅ **Secure Assessment**: No answer exposure during interviews
- ✅ **Independent Scaling**: Deploy and scale services separately
- ✅ **Database Integration**: PostgreSQL with JSON response storage

## 🔧 Local Testing

See `RAILWAY_DEPLOYMENT_GUIDE.md` for complete local testing instructions.

Ready for Railway deployment! 🚀