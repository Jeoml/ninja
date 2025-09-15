# Round 1 Quiz Agent

An intelligent quiz system that adapts to user performance and tracks topic mastery.

## Features

🎯 **Adaptive Question Selection**: Intelligently selects questions from different topics  
📊 **Performance Tracking**: Tracks solved vs unsolved topics  
🧠 **Smart Catalog**: If a topic is both solved and unsolved, marks it as solved  
💬 **Chat Interface**: Conversational API design for better UX  
📈 **Progress Monitoring**: Real-time performance analytics  

## Architecture

```
round1/
├── api.py                 # FastAPI routes and chat interface
├── quiz_service.py        # Main quiz orchestration logic
├── catalog_service.py     # Topic performance tracking
├── database_service.py    # Question fetching from database
├── models.py              # Pydantic models for API
└── README.md              # This file
```

## Quiz Flow

1. **Start Session**: `POST /ai-agents/round1/start`
2. **Get Question**: `GET /ai-agents/round1/question`
3. **Submit Answer**: `POST /ai-agents/round1/answer`
4. **Repeat 2-3** until 10-15 questions completed
5. **View Results**: `GET /ai-agents/round1/performance`

## API Endpoints

### Core Quiz Flow
- `POST /ai-agents/round1/start` - Start new quiz session
- `GET /ai-agents/round1/question` - Get next question
- `POST /ai-agents/round1/answer` - Submit answer (A/B/C/D)
- `GET /ai-agents/round1/performance` - Current performance
- `GET /ai-agents/round1/status` - Quiz session status
- `POST /ai-agents/round1/end` - End session early
- `POST /ai-agents/round1/reset` - Reset session

### Chat Interface
- `GET /ai-agents/round1/chat/intro` - Friendly introduction
- `GET /ai-agents/round1/chat/help` - Usage help

## Key Logic

### Topic Catalog Rules
- ✅ **Solved**: Only correct answers for this topic
- ❌ **Unsolved**: Only incorrect answers for this topic  
- ✅ **Mixed → Solved**: Both correct AND incorrect answers (per requirement)

### Question Selection Strategy
1. **Priority 1**: Unattempted topics
2. **Priority 2**: Topics needing more attempts
3. **Priority 3**: Random from available pool
4. **Diversity**: Tries to cover different topics

### Performance Tracking
```json
{
  "total_questions": 12,
  "correct_answers": 8,
  "incorrect_answers": 4,
  "accuracy": 0.67,
  "topics_attempted": 6,
  "solved_topics": ["Formulas", "Charts"],
  "unsolved_topics": ["VBA", "Data Analysis"],
  "topic_breakdown": {
    "Formulas": {
      "correct": 3,
      "incorrect": 0,
      "total": 3,
      "accuracy": 1.0,
      "status": "solved"
    }
  }
}
```

## Usage Examples

### Start a Quiz
```bash
curl -X POST "http://localhost:8000/ai-agents/round1/start" \
  -H "Content-Type: application/json" \
  -d '{"max_questions": 12}'
```

### Get Next Question
```bash
curl "http://localhost:8000/ai-agents/round1/question"
```

### Submit Answer
```bash
curl -X POST "http://localhost:8000/ai-agents/round1/answer" \
  -H "Content-Type: application/json" \
  -d '{"answer": "B"}'
```

### Check Performance
```bash
curl "http://localhost:8000/ai-agents/round1/performance"
```

## Database Integration

Connects to the same PostgreSQL database as the auth system:
- Fetches only **easy** difficulty questions
- Ensures topic diversity
- Avoids question repetition within session
- Supports 45+ easy questions across 10+ topics

## Smart Features

### Intelligent Question Selection
- Prioritizes unexplored topics
- Balances topic coverage
- Avoids immediate repetition
- Adapts based on performance

### Performance Analytics
- Real-time accuracy tracking
- Topic-wise performance breakdown
- Study recommendations
- Progress visualization

### Chat-like Experience
- Friendly introductions
- Helpful explanations
- Progress updates
- Encouraging feedback

## Error Handling

- Validates answer format (A/B/C/D only)
- Handles database connection issues
- Manages session state properly
- Provides clear error messages

## Future Enhancements

- User authentication integration
- Persistent session storage
- Advanced analytics dashboard
- Difficulty progression
- Multiplayer competitions
