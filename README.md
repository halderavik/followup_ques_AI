# Survey Intelligence API - MVP

## Overview
This project is a Flask-based REST API that generates intelligent follow-up questions for open-ended survey responses using OpenAI GPT-4o-mini. It is designed for easy integration with survey platforms and provides exactly 3 contextually relevant follow-up questions per response with specific types: Reason, Example, and Impact. The API also includes enhanced multilingual support with informativeness detection and **theme-enhanced analysis**.

## Features
- AI-powered question generation (OpenAI GPT-4o-mini)
- **Exactly 3 follow-up questions** with specific types: Reason, Example, Impact
- **Enhanced multilingual support** with informativeness detection
- **🆕 Theme-enhanced analysis** - detects themes in responses and generates contextually relevant questions
- **🆕 Non-overlapping question types** - strict adherence to question type boundaries (elaboration questions never contain examples)
- **🆕 Intelligent validation and fixing** - automatic detection and correction of question type compliance issues
- **Informativeness detection** - automatically detects non-informative responses (e.g., "I don't know", "no")
- **Theme detection and ranking** - identifies themes by importance and generates targeted questions
- Simple REST API (JSON)
- No authentication required for users
- Comprehensive error handling
- Intelligent follow-up question generation
- Type mapping and fallback mechanisms for reliable output
- Support for multiple languages (English, Chinese, Japanese, Spanish, French, German, Korean)

## Tech Stack
- Python 3.11
- Flask 2.3.3
- Pydantic 2.4.2
- Requests 2.31.0
- python-dotenv
- pytest, Black, Flake8

## 🚀 Live Deployment
**Production URL:** `https://followup-ai-questions-e534ed0185cb.herokuapp.com/`

## Setup Instructions
1. Clone the repository and navigate to the project directory.
2. Create a Python 3.11 virtual environment:
   ```bash
   py -3.11 -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   
   # Windows Command Prompt
   .\venv\Scripts\activate.bat
   
   # Linux/Mac
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the project root with your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   **⚠️ Security Note**: Never commit your actual API key to Git. The `.env` file is already in `.gitignore`.
6. Run the Flask app:
   ```bash
   python main.py
   ```
7. Test the API:
   ```bash
   # API information
   curl http://localhost:5000/
   
   # Health check
   curl http://localhost:5000/health
   
   # Get question types
   curl http://localhost:5000/question-types
   
   # Generate follow-up questions
   curl -X POST http://localhost:5000/generate-followup \
     -H "Content-Type: application/json" \
     -d '{"question": "What did you think?", "response": "It was good."}'
   ```

## Project Structure
- `app/` - Main application code
  - `__init__.py` - Flask app factory
  - `routes.py` - API endpoints
  - `models.py` - Pydantic data models
  - `question_types.py` - Question type enums
  - `error_models.py` - Error response models
  - `deepseek_service.py` - OpenAI LLM integration with validation and fixing logic
  - `log_config.py` - Logging configuration
- `tests/` - Unit and integration tests
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (OpenAI API key)
- `.python-version` - Python version specification for Heroku
- `README.md` - Project documentation
- `API.md` - Comprehensive API documentation
- `Survey_Intelligence_API.postman_collection.json` - Postman collection
- `POSTMAN_TESTING_GUIDE.md` - Testing guide

## API Endpoints

### GET `/`
Returns API information and available endpoints.

### GET `/health`
Health check endpoint. Returns `{"status": "ok"}`.

### GET `/question-types`
Returns all supported follow-up question types.

### POST `/generate-followup`
Generates intelligent follow-up questions based on survey responses with strict type adherence. Supports all 6 question types with non-overlapping boundaries.

**Request Body:**
```json
{
  "question": "What did you think of our service?",
  "response": "The service was good but could be faster.",
  "allowed_types": ["reason", "elaboration", "impact"]
}
```

**Response:**
```json
{
  "followups": [
    {
      "text": "Why do you think the service could be faster?",
      "type": "reason"
    },
    {
      "text": "Can you tell me more about what aspects of the service felt slow?",
      "type": "elaboration"
    },
    {
      "text": "How did the speed of the service impact your overall experience?",
      "type": "impact"
    }
  ]
}
```

### POST `/generate-multilingual`
Generates a single follow-up question in the specified language with strict type compliance.

**Request Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management.",
  "type": "elaboration",
  "language": "English"
}
```

**Response:**
```json
{
  "question": "Can you tell me more about your time management challenges at work?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management.",
  "type": "elaboration",
  "language": "English"
}
```

### POST `/generate-enhanced-multilingual`
Generates a single follow-up question in the specified language with informativeness detection and type validation.

**Request Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I don't know",
  "type": "elaboration",
  "language": "English"
}
```

**Response (Non-informative):**
```json
{
  "informative": 0,
  "question": null,
  "original_question": "What challenges do you face at work?",
  "original_response": "I don't know",
  "type": "elaboration",
  "language": "English"
}
```

**Response (Informative):**
```json
{
  "informative": 1,
  "question": "Can you tell me more about your time management challenges at work?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management.",
  "type": "elaboration",
  "language": "English"
}
```

### 🆕 POST `/generate-theme-enhanced`
**NEW!** Generates a theme-enhanced multilingual follow-up question with intelligent theme analysis and strict type compliance.

**Request Body (Theme Analysis Enabled):**
```json
{
  "question": "How do you communicate with your team?",
  "response": "I use email and Slack for most communications, but sometimes face-to-face meetings are more effective.",
  "type": "elaboration",
  "language": "English",
  "theme": "Yes",
  "theme_parameters": {
    "themes": [
      {"name": "communication", "importance": 80},
      {"name": "leadership", "importance": 60},
      {"name": "collaboration", "importance": 70}
    ]
  }
}
```

**Response (Theme Found):**
```json
{
  "informative": 1,
  "question": "Can you tell me more about when face-to-face meetings are more effective than digital communication for your team?",
  "explanation": "This question focuses on the theme of 'communication' by asking the user to elaborate on their preference for face-to-face interactions...",
  "original_question": "How do you communicate with your team?",
  "original_response": "I use email and Slack for most communications, but sometimes face-to-face meetings are more effective.",
  "type": "elaboration",
  "language": "English",
  "theme": "Yes",
  "detected_theme": "communication",
  "theme_importance": 80,
  "highest_importance_theme": null
}
```

### 🆕 POST `/generate-theme-enhanced-optional`
**NEW!** Theme-enhanced API with optional informativeness checking and enhanced type validation.

**Request Body:**
```json
{
  "question": "What are the main reasons you prefer to use your business credit?",
  "response": "helps with the credit score",
  "type": "elaboration",
  "language": "English",
  "theme": "Yes",
  "check_informative": false,
  "theme_parameters": {
    "themes": [
      {"name": "To Keep Business or Personal Expenses Separate", "importance": 80},
      {"name": "Helps To Build Business Credit or Reputation", "importance": 60}
    ]
  }
}
```

## 🎯 Enhanced Features

### Non-Overlapping Question Types
- **Strict type boundaries** - Each question type has clear, non-overlapping definitions
- **Automatic validation** - Questions are validated for type compliance after generation
- **Intelligent fixing** - Non-compliant questions are automatically corrected
- **Type-specific keywords** - Each type uses appropriate keywords and avoids forbidden terms

### Question Type Definitions
- **Reason**: Focuses on WHY they think/feel this way (avoids examples, details, effects)
- **Clarification**: CLARIFIES unclear terms or concepts (avoids examples, details, reasons)
- **Elaboration**: Asks for MORE DETAILS about their response (avoids examples, reasons, effects)
- **Example**: Requests SPECIFIC EXAMPLES or instances (avoids reasons, details, effects)
- **Impact**: Explores EFFECTS or CONSEQUENCES (avoids reasons, examples, details)
- **Comparison**: Asks for COMPARISON with alternatives (avoids reasons, examples, details)

### Theme Detection
- Automatically detects themes in survey responses
- Ranks themes by importance (0-100%)
- Generates questions based on detected themes
- Provides graceful fallback when no themes are found

### Missing Theme Handling
- When no themes are found, asks about highest importance theme
- Provides graceful fallback mechanisms
- Maintains conversation flow

### Multilingual Theme Support
- Theme detection works across all supported languages
- Generates culturally appropriate questions
- Maintains language consistency

### Explanation Generation
- Provides detailed explanations for question generation
- Explains theme detection and reasoning
- Helps understand AI decision-making

## Supported Languages
- English
- Chinese (中文)
- Japanese (日本語)
- Spanish (Español)
- French (Français)
- German (Deutsch)
- Korean (한국어)

## Testing
Run the comprehensive test suite:
```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_api.py
python -m pytest tests/test_deepseek_service.py
```

## Recent Updates
- ✅ **Non-overlapping question types** - Strict adherence to question type boundaries
- ✅ **Enhanced validation and fixing** - Automatic detection and correction of compliance issues
- ✅ **Improved prompt engineering** - Updated all endpoints with strict type boundaries
- ✅ **Directory cleanup** - Removed temporary test files and documentation
- ✅ **Python version management** - Migrated to `.python-version` for Heroku compatibility

## License
MIT (or specify as appropriate) 