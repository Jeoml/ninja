# LangGraph Service

AI-Powered Adaptive Quiz Agent with Question Generation.

## Features

- **6-Node LangGraph Workflow**: Intelligent adaptive assessment
- **AI Question Generation**: Creates new questions based on user performance
- **User Profiling**: Comprehensive psychological and educational analysis
- **Groq Integration**: Uses Qwen 3-32B model for AI interactions
- **Self-Improving**: Questionnaire evolves with each assessment

## Environment Variables

Set these in Railway:

```
BACKEND_SERVICE_URL=https://your-backend-service.railway.app
GROQ_API_KEY=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
DATABASE_URL=postgresql://...
PORT=8001
```

## API Endpoints

- `POST /ai-agents/langgraph/start-quiz` - Start adaptive assessment
- `GET /ai-agents/langgraph/user-summary/{session_id}` - Get user summary
- `GET /ai-agents/langgraph/health` - Health check
- `GET /ai-agents/langgraph/info` - Agent information

## Workflow

1. **Node 1**: Initial shortcuts question
2. **Node 2**: Check user response
3. **Node 3A**: Correct answer followup (2 easy + 2 medium)
4. **Node 3B**: Topic catalog analysis
5. **Node 4**: Select new random topic
6. **Node 5**: Ask question on selected topic
7. **Node 6**: Generate new questions + user summary

## Deployment

Deploy to Railway:
1. Connect this folder as a separate Railway service
2. Set environment variables (especially BACKEND_SERVICE_URL)
3. Deploy
