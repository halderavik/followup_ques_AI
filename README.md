# Survey Intelligence API - MVP

## Overview
This project is a Flask-based REST API that generates intelligent follow-up questions for open-ended survey responses using DeepSeek LLM. It is designed for easy integration with survey platforms and provides exactly 3 contextually relevant follow-up questions per response with specific types: Reason, Example, and Impact. The API also includes enhanced multilingual support with informativeness detection and **theme-enhanced analysis**.

## Features
- AI-powered question generation (DeepSeek LLM)
- **Exactly 3 follow-up questions** with specific types: Reason, Example, Impact
- **Enhanced multilingual support** with informativeness detection
- **🆕 Theme-enhanced analysis** - detects themes in responses and generates contextually relevant questions
- **Informativeness detection** - automatically detects non-informative responses (e.g., "I don't know", "no")
- **Theme detection and ranking** - identifies themes by importance and generates targeted questions
- Simple REST API (JSON)
- No authentication required for users
- Comprehensive error handling
- Intelligent follow-up question generation
- Type mapping and fallback mechanisms for reliable output
- Support for multiple languages (English, Chinese, Japanese, Spanish, French, German, Korean)

## Tech Stack
- Python 3.9+
- Flask 2.3.3
- Pydantic 2.4.2
- Requests 2.31.0
- python-dotenv
- pytest, Black, Flake8

## 🚀 Live Deployment
**Production URL:** `https://follow-up-question-f00b29aae45c.herokuapp.com/`

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
5. Create a `.env` file in the project root with your DeepSeek API key:
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
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
  - `deepseek_service.py` - DeepSeek LLM integration
  - `log_config.py` - Logging configuration
- `tests/` - Unit and integration tests
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (DeepSeek API key)
- `README.md` - Project documentation
- `Survey_Intelligence_API.postman_collection.json` - Postman collection
- `POSTMAN_TESTING_GUIDE.md` - Testing guide
- `run_tests.py` - Custom test runner

## API Endpoints

### GET `/`
Returns API information and available endpoints.

### GET `/health`
Health check endpoint. Returns `{"status": "ok"}`.

### GET `/question-types`
Returns all supported follow-up question types.

### POST `/generate-followup`
Generates exactly 3 intelligent follow-up questions based on survey responses with specific types: Reason, Example, and Impact.

**Request Body:**
```json
{
  "question": "What did you think of our service?",
  "response": "The service was good but could be faster."
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
      "text": "Can you give examples of when the service felt slow?",
      "type": "example"
    },
    {
      "text": "How did the speed of the service impact your overall experience?",
      "type": "impact"
    }
  ]
}
```

### POST `/generate-multilingual`
Generates a single follow-up question in the specified language.

**Request Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management.",
  "type": "reason",
  "language": "English"
}
```

**Response:**
```json
{
  "question": "Why do you struggle with time management?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management.",
  "type": "reason",
  "language": "English"
}
```

### POST `/generate-enhanced-multilingual`
Generates a single follow-up question in the specified language with informativeness detection. If the response is non-informative, no question is generated.

**Request Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I don't know",
  "type": "reason",
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
  "type": "reason",
  "language": "English"
}
```

**Response (Informative):**
```json
{
  "informative": 1,
  "question": "Why do you struggle with time management?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management.",
  "type": "reason",
  "language": "English"
}
```

### 🆕 POST `/generate-theme-enhanced`
**NEW!** Generates a theme-enhanced multilingual follow-up question with intelligent theme analysis. Detects themes in responses and generates contextually relevant questions based on theme importance.

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
  "question": "Can you give an example of a situation where face-to-face meetings were more effective than digital communication for your team?",
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

**Request Body (Standard Mode - No Theme Analysis):**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management and communication.",
  "type": "reason",
  "language": "English",
  "theme": "No"
}
```

**Response (Standard Mode):**
```json
{
  "informative": 1,
  "question": "Why do you struggle with time management and communication at work?",
  "explanation": null,
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management and communication.",
  "type": "reason",
  "language": "English",
  "theme": "No",
  "detected_theme": null,
  "theme_importance": null,
  "highest_importance_theme": null
}
```

**Response (No Theme Found - Uses Highest Importance Theme):**
```json
{
  "informative": 1,
  "question": "Do you think the calming effect of blue relates to how it might influence communication or social interactions?",
  "explanation": "This question gently introduces the missing theme of 'communication' by connecting it to the user's stated preference...",
  "original_question": "What's your favorite color?",
  "original_response": "I like blue because it's calming.",
  "type": "reason",
  "language": "English",
  "theme": "Yes",
  "detected_theme": null,
  "theme_importance": null,
  "highest_importance_theme": "communication"
}
```

## 🎯 Theme-Enhanced API Features

### Theme Detection
- Automatically detects themes in survey responses
- Ranks themes by importance (0-100%)
- Generates questions based on detected themes

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
Run comprehensive tests for the theme-enhanced API:
```bash
python test_theme_api_comprehensive.py
```

## License
MIT (or specify as appropriate) 