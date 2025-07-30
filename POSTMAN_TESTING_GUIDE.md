# Postman Testing Guide - Survey Intelligence API

## Setup Instructions

### 1. Import the Collection
1. Open Postman
2. Click "Import" button
3. Select the `Survey_Intelligence_API.postman_collection.json` file
4. The collection will be imported with all endpoints ready to test

### 2. Start the Flask App
Make sure your Flask application is running:
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start the app
python main.py
```

The app should be running on `http://localhost:5000`

## Testing the Endpoints

### 1. API Information
**Request:** `GET http://localhost:5000/`

**Expected Response:**
```json
{
  "name": "Survey Intelligence API",
  "description": "Generate intelligent follow-up questions for survey responses using DeepSeek AI",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "question_types": "/question-types",
    "generate_followup": "/generate-followup",
    "generate_multilingual": "/generate-multilingual",
    "generate_enhanced_multilingual": "/generate-enhanced-multilingual"
  },
  "usage": {
    "health": "GET /health - Check API status",
    "question_types": "GET /question-types - Get available question types",
    "generate_followup": "POST /generate-followup - Generate follow-up questions",
    "generate_multilingual": "POST /generate-multilingual - Generate multilingual questions",
    "generate_enhanced_multilingual": "POST /generate-enhanced-multilingual - Generate multilingual questions with informativeness detection"
  }
}
```
**Status Code:** 200

**Purpose:** Get API information and available endpoints

---

### 2. Health Check
**Request:** `GET http://localhost:5000/health`

**Expected Response:**
```json
{
  "status": "ok"
}
```
**Status Code:** 200

**Purpose:** Verify the API is running and healthy

---

### 2. Get Question Types
**Request:** `GET http://localhost:5000/question-types`

**Expected Response:**
```json
{
  "question_types": [
    "reason",
    "clarification", 
    "elaboration",
    "example",
    "impact",
    "comparison"
  ]
}
```
**Status Code:** 200

**Purpose:** Get all supported follow-up question types

---

### 3. Generate Follow-up Questions - Basic
**Request:** `POST http://localhost:5000/generate-followup`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "question": "What did you think of our service?",
  "response": "The service was good but could be faster."
}
```

**Expected Response:**
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
**Status Code:** 200

**Note:** This endpoint always returns exactly 3 questions with the types: reason, example, and impact.

---

### 4. Generate Follow-up Questions - Different Topic
**Request:** `POST http://localhost:5000/generate-followup`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "question": "How satisfied are you with our product?",
  "response": "I'm satisfied with the features but the price is too high."
}
```

**Expected Response:**
```json
{
  "followups": [
    {
      "text": "Why do you think the price is too high compared to the features?",
      "type": "reason"
    },
    {
      "text": "Can you provide examples of similar products and their pricing?",
      "type": "example"
    },
    {
      "text": "How does the high price impact your decision to continue using the product?",
      "type": "impact"
    }
  ]
}
```
**Status Code:** 200

**Purpose:** Test with different content to verify consistent 3-question output

---



---

### 5. Generate Follow-up Questions - Invalid Data
**Request:** `POST http://localhost:5000/generate-followup`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "question": "",
  "response": ""
}
```

**Expected Response:**
```json
{
  "code": "validation_error",
  "detail": "Invalid request data.",
  "errors": [
    {
      "loc": ["question"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["response"],
      "msg": "field required", 
      "type": "value_error.missing"
    }
  ]
}
```
**Status Code:** 422

**Purpose:** Test input validation

---

### 6. Generate Multilingual Question
**Request:** `POST http://localhost:5000/generate-multilingual`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management.",
  "type": "reason",
  "language": "English"
}
```

**Expected Response:**
```json
{
  "question": "Why do you struggle with time management?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management.",
  "type": "reason",
  "language": "English"
}
```
**Status Code:** 200

**Purpose:** Test multilingual question generation

---

### 7. Generate Enhanced Multilingual Question - Informative Response
**Request:** `POST http://localhost:5000/generate-enhanced-multilingual`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management and communication.",
  "type": "reason",
  "language": "English"
}
```

**Expected Response:**
```json
{
  "informative": 1,
  "question": "Why do you struggle with time management and communication?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management and communication.",
  "type": "reason",
  "language": "English"
}
```
**Status Code:** 200

**Purpose:** Test enhanced multilingual with informative response

---

### 8. Generate Enhanced Multilingual Question - Non-informative Response
**Request:** `POST http://localhost:5000/generate-enhanced-multilingual`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I don't know",
  "type": "reason",
  "language": "English"
}
```

**Expected Response:**
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
**Status Code:** 200

**Purpose:** Test enhanced multilingual with non-informative response (informativeness detection)

---

### 9. Generate Theme-Enhanced Question - Theme Found
**Request:** `POST http://localhost:5000/generate-theme-enhanced`

**Headers:**
```
Content-Type: application/json
```

**Body:**
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

**Expected Response:**
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
**Status Code:** 200

**Purpose:** Test theme-enhanced API with theme detection

---

### 10. Generate Theme-Enhanced Question - No Theme Found
**Request:** `POST http://localhost:5000/generate-theme-enhanced`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "question": "What's your favorite color?",
  "response": "I like blue because it's calming.",
  "type": "reason",
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

**Expected Response:**
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
**Status Code:** 200

**Purpose:** Test theme-enhanced API when no theme is found (uses highest importance theme)

---

### 11. Generate Theme-Enhanced Question - Standard Mode
**Request:** `POST http://localhost:5000/generate-theme-enhanced`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management and communication.",
  "type": "reason",
  "language": "English",
  "theme": "No"
}
```

**Expected Response:**
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
**Status Code:** 200

**Purpose:** Test theme-enhanced API in standard mode (no theme analysis)

## Testing Workflow

1. **Start with API Information** - Get overview of available endpoints
2. **Health Check** - Verify the API is running
3. **Get Question Types** - See available question types
4. **Test Validation** - Try the "Invalid Data" request to see 422 error
5. **Test Main Functionality** - Try the basic and with-types requests to see generated questions
6. **Test Multilingual** - Test the multilingual endpoint
7. **Test Enhanced Multilingual** - Test both informative and non-informative responses
8. **Test Theme-Enhanced API** - Test theme detection, missing themes, and standard mode

## Expected Behavior Summary

| Endpoint | Auth Required | Expected Status | Notes |
|----------|---------------|-----------------|-------|
| `/` | No | 200 | Returns API information and endpoints |
| `/health` | No | 200 | Always returns `{"status": "ok"}` |
| `/question-types` | No | 200 | Returns all 6 question types |
| `/generate-followup` | No | 200 | Returns intelligent follow-up questions |
| `/generate-followup` (invalid data) | No | 422 | Validation error |
| `/generate-multilingual` | No | 200 | Returns multilingual follow-up question |
| `/generate-enhanced-multilingual` | No | 200 | Returns enhanced multilingual with informativeness detection |
| `/generate-theme-enhanced` | No | 200 | Returns theme-enhanced questions with theme analysis |

## Troubleshooting

### Common Issues:

1. **Connection Refused (ECONNREFUSED)**
   - Make sure Flask app is running on port 5000
   - Check if another service is using port 5000

2. **404 Not Found**
   - Verify the URL is correct: `http://localhost:5000/health`
   - Check if the Flask app started successfully

3. **401 Unauthorized**
   - This should not happen - no authentication is required
   - If you see this, there may be an issue with the API configuration

4. **502 Bad Gateway**
   - This should not happen with the current implementation
   - If you see this, check your DeepSeek API key in the `.env` file

### Environment Variables:
Make sure your `.env` file contains the DeepSeek API key (this is used server-side only):
```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## Next Steps

Once you've verified all endpoints work as expected, you can:
1. Test with different survey scenarios and question types
2. Integrate with your survey platform
3. Deploy to production
4. Monitor API usage and response quality 