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
    "generate_followup": "/generate-followup"
  },
  "usage": {
    "health": "GET /health - Check API status",
    "question_types": "GET /question-types - Get available question types",
    "generate_followup": "POST /generate-followup - Generate follow-up questions"
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

## Testing Workflow

1. **Start with API Information** - Get overview of available endpoints
2. **Health Check** - Verify the API is running
3. **Get Question Types** - See available question types
4. **Test Validation** - Try the "Invalid Data" request to see 422 error
5. **Test Main Functionality** - Try the basic and with-types requests to see generated questions

## Expected Behavior Summary

| Endpoint | Auth Required | Expected Status | Notes |
|----------|---------------|-----------------|-------|
| `/` | No | 200 | Returns API information and endpoints |
| `/health` | No | 200 | Always returns `{"status": "ok"}` |
| `/question-types` | No | 200 | Returns all 6 question types |
| `/generate-followup` | No | 200 | Returns intelligent follow-up questions |
| `/generate-followup` (invalid data) | No | 422 | Validation error |

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