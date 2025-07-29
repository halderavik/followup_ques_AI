# 📊 Survey Intelligence API Documentation

## Overview

The Survey Intelligence API generates intelligent follow-up questions for open-ended survey responses using advanced AI. This API is designed to integrate seamlessly with survey platforms like **Qualtrics**, **SurveyMonkey**, and other survey tools to enhance data collection and respondent engagement.

**Live API URL**: `https://follow-up-question-f00b29aae45c.herokuapp.com/`

## 🎯 Use Cases

### Survey Platform Integration
- **Qualtrics**: Generate dynamic follow-up questions based on open-ended responses
- **SurveyMonkey**: Enhance respondent engagement with intelligent probing
- **Custom Surveys**: Add AI-powered question generation to any survey tool
- **Research Studies**: Improve data quality through targeted follow-up questions

### Common Scenarios
- Customer feedback surveys
- Market research questionnaires
- Employee satisfaction surveys
- Academic research studies
- Product evaluation forms

## 🔗 API Endpoints

### Base URL
```
https://follow-up-question-f00b29aae45c.herokuapp.com
```

### 1. API Information
**GET** `/`

Returns basic API information and available endpoints.

**Response:**
```json
{
  "name": "Survey Intelligence API",
  "version": "1.0.0",
  "description": "AI-powered follow-up question generation for surveys",
  "endpoints": {
    "health": "/health",
    "question_types": "/question-types",
    "generate_followup": "/generate-followup",
    "generate_reason": "/generate-reason",
    "generate_multilingual": "/generate-multilingual"
  }
}
```

### 2. Health Check
**GET** `/health`

Verifies API status and connectivity.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. Available Question Types
**GET** `/question-types`

Returns all supported question types for follow-up generation.

**Response:**
```json
{
  "question_types": [
    "REASON",
    "CLARIFICATION", 
    "ELABORATION",
    "EXAMPLE",
    "IMPACT",
    "COMPARISON"
  ]
}
```

### 4. Generate Follow-up Questions
**POST** `/generate-followup`

Generates exactly 3 intelligent follow-up questions with specific types: Reason, Example, and Impact.

**Request Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management and communication with my team."
}
```

**Response:**
```json
{
  "followups": [
    {
      "text": "Why do you think time management and communication are challenging for you?",
      "type": "reason"
    },
    {
      "text": "Can you give examples of when time management and communication issues arise?",
      "type": "example"
    },
    {
      "text": "How do these challenges impact your work performance and team dynamics?",
      "type": "impact"
    }
  ]
}
```

**Note:** This endpoint always returns exactly 3 questions with the types: reason, example, and impact. The `allowed_types` parameter is no longer used as the types are fixed.

### 5. Generate Single Reason Question
**POST** `/generate-reason`

Generates a single reason-based follow-up question for deeper understanding.

**Request Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management and communication."
}
```

**Response:**
```json
{
  "question": "Why do you think time management and communication are challenging for you?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management and communication with my team."
}
```

### 6. Generate Multilingual Question
**POST** `/generate-multilingual`

Generates a single follow-up question in the specified language. The original question and response should be in the same language as the target language.

**Request Body:**
```json
{
  "question": "你在工作中面临什么挑战？",
  "response": "我在时间管理和沟通方面有困难。",
  "type": "reason",
  "language": "Chinese"
}
```

**Response:**
```json
{
  "question": "为什么你觉得时间管理和沟通对你来说是挑战呢？",
  "original_question": "你在工作中面临什么挑战？",
  "original_response": "我在时间管理和沟通方面有困难。",
  "type": "reason",
  "language": "Chinese"
}
```

**Supported Languages:**
- Chinese (中文)
- Japanese (日本語)
- Spanish (Español)
- French (Français)
- German (Deutsch)
- Korean (한국어)
- And more (any language DeepSeek supports)

**Supported Question Types:**
- `reason` - Ask why
- `impact` - Ask about effects
- `elaboration` - Ask for details
- `example` - Ask for examples
- `clarification` - Ask for clarification
- `comparison` - Ask for comparison

## 🔧 Integration Guide

### Qualtrics Integration

#### Method 1: Using Qualtrics JavaScript
```javascript
// Add this to your Qualtrics survey's JavaScript
Qualtrics.SurveyEngine.addOnload(function() {
    // Trigger when respondent submits an open-ended response
    var questionId = this.questionId;
    
    // Get the response text
    var response = $('QR~' + questionId).value;
    
    // Call our API
    fetch('https://follow-up-question-f00b29aae45c.herokuapp.com/generate-followup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            question: "What challenges do you face at work?",
            response: response
        })
    })
    .then(response => response.json())
    .then(data => {
        // Display follow-up questions
        data.followups.forEach(q => {
            // Create new question elements
            console.log(`${q.type}: ${q.text}`);
        });
    });
});
```

#### Method 2: Using Qualtrics Piped Text
```javascript
// Store API response in embedded data
Qualtrics.SurveyEngine.addOnload(function() {
    var response = $('QR~QID1').value;
    
    fetch('https://follow-up-question-f00b29aae45c.herokuapp.com/generate-followup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question: "${e://Field/original_question}",
            response: response
        })
    })
    .then(r => r.json())
    .then(data => {
        Qualtrics.SurveyEngine.setEmbeddedData('followup_1', data.followups[0].text);
        Qualtrics.SurveyEngine.setEmbeddedData('followup_2', data.followups[1].text);
        Qualtrics.SurveyEngine.setEmbeddedData('followup_3', data.followups[2].text);
    });
});
```

### SurveyMonkey Integration

#### Using SurveyMonkey Webhooks
```javascript
// Webhook endpoint to receive survey responses
app.post('/webhook/surveymonkey', (req, res) => {
    const response = req.body;
    
    // Extract open-ended response
    const answer = response.answers.find(a => a.question_type === 'text');
    
    if (answer) {
        // Generate follow-up questions
        fetch('https://follow-up-question-f00b29aae45c.herokuapp.com/generate-followup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: answer.question_text,
                response: answer.text
            })
        })
        .then(r => r.json())
        .then(data => {
            // Send follow-up questions via email or SMS
            sendFollowupQuestions(response.respondent_id, data.followups);
        });
    }
    
    res.status(200).send('OK');
});
```

### General HTTP Integration

#### cURL Example
```bash
curl -X POST https://follow-up-question-f00b29aae45c.herokuapp.com/generate-followup \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is your favorite programming language?",
    "response": "I love Python because it is easy to learn and has great libraries."
  }'
```

#### cURL Example for Single Reason Question
```bash
curl -X POST https://follow-up-question-f00b29aae45c.herokuapp.com/generate-reason \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What challenges do you face at work?",
    "response": "I struggle with time management and communication."
  }'
```

#### Python Example
```python
import requests
import json

def generate_followup_questions(question, response):
    url = "https://follow-up-question-f00b29aae45c.herokuapp.com/generate-followup"
    
    payload = {
        "question": question,
        "response": response
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code}")

# Usage example
try:
    result = generate_followup_questions(
        question="What challenges do you face at work?",
        response="I struggle with time management and communication."
    )
    
    for q in result['followups']:
        print(f"{q['type']}: {q['text']}")
        
except Exception as e:
    print(f"Error: {e}")

# Single reason question example
def generate_single_reason_question(question, response):
    url = "https://follow-up-question-f00b29aae45c.herokuapp.com/generate-reason"
    
    payload = {
        "question": question,
        "response": response
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code}")

# Usage example for single reason question
try:
    result = generate_single_reason_question(
        question="What challenges do you face at work?",
        response="I struggle with time management and communication."
    )
    
    print(f"Generated question: {result['question']}")
        
except Exception as e:
    print(f"Error: {e}")

#### JavaScript/Node.js Example
```javascript
const axios = require('axios');

async function generateFollowupQuestions(question, response) {
    try {
        const apiResponse = await axios.post(
            'https://follow-up-question-f00b29aae45c.herokuapp.com/generate-followup',
            {
                question: question,
                response: response
            },
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );
        
        return apiResponse.data;
    } catch (error) {
        throw new Error(`API Error: ${error.response?.status || error.message}`);
    }
}

// Usage example
async function main() {
    try {
        const result = await generateFollowupQuestions(
            "What challenges do you face at work?",
            "I struggle with time management and communication."
        );
        
        result.followups.forEach(q => {
            console.log(`${q.type}: ${q.text}`);
        });
        
    } catch (error) {
        console.error(`Error: ${error.message}`);
    }
}

main();
```

// Single reason question example
async function generateSingleReasonQuestion(question, response) {
    try {
        const result = await axios.post(
            'https://follow-up-question-f00b29aae45c.herokuapp.com/generate-reason',
            {
                question: question,
                response: response
            },
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );
        
        return result.data;
    } catch (error) {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
    }
}

// Usage example for single reason question
generateSingleReasonQuestion(
    "What challenges do you face at work?",
    "I struggle with time management and communication."
)
.then(result => {
    console.log(`Generated question: ${result.question}`);
})
.catch(error => {
    console.error('Error:', error);
});

## 📋 Question Types Reference

| Type | Description | Example |
|------|-------------|---------|
| **REASON** | Asks for the underlying cause or motivation | "Why do you prefer this approach?" |
| **CLARIFICATION** | Seeks to clarify ambiguous or unclear points | "Can you clarify what you mean by 'efficient'?" |
| **ELABORATION** | Requests more detailed information | "Can you tell me more about your experience?" |
| **EXAMPLE** | Asks for specific examples or instances | "Can you provide an example of this situation?" |
| **IMPACT** | Explores consequences or effects | "How does this affect your daily routine?" |
| **COMPARISON** | Asks for comparisons with alternatives | "How does this compare to other options?" |

## 🔄 Workflow Examples

### Customer Feedback Survey
```json
{
  "question": "What do you think about our product?",
  "answer": "The interface is confusing and it's too slow.",
  "question_types": ["CLARIFICATION", "EXAMPLE", "IMPACT"]
}
```

**Generated Follow-ups:**
1. "What specific aspects of the interface do you find confusing?"
2. "Can you provide an example of when the slowness was most noticeable?"
3. "How does the confusing interface and slowness impact your overall user experience?"

### Employee Satisfaction Survey
```json
{
  "question": "How satisfied are you with your work environment?",
  "answer": "I like my colleagues but the office space is too crowded.",
  "question_types": ["REASON", "EXAMPLE", "COMPARISON"]
}
```

**Generated Follow-ups:**
1. "What makes you enjoy working with your colleagues?"
2. "Can you describe a specific situation where the crowded office space was problematic?"
3. "How does this work environment compare to your previous workplaces?"

### Single Reason Question Example
```json
{
  "question": "What do you think about our product?",
  "response": "The interface is confusing and it's too slow."
}
```

**Generated Reason Question:**
"Why do you find the interface confusing and slow?"

## ⚠️ Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": "Missing required field: question"
}
```

#### 422 Unprocessable Entity
```json
{
  "error": "Invalid question type",
  "details": "Question type 'INVALID_TYPE' is not supported"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "Unable to generate follow-up questions"
}
```

### Best Practices
1. **Always handle errors gracefully** in your integration
2. **Implement retry logic** for transient failures
3. **Validate input** before sending to the API
4. **Cache responses** when appropriate to reduce API calls
5. **Monitor API usage** and implement rate limiting if needed

## 📊 Rate Limits & Performance

- **No rate limits** currently applied
- **Response time**: Typically 2-5 seconds
- **Availability**: 99.9% uptime
- **Recommended**: Implement client-side caching for repeated requests

## 🔐 Security

- **No authentication required** for public use
- **HTTPS only** - all endpoints use SSL/TLS
- **Input validation** on all endpoints
- **CORS enabled** for web integrations

## 📞 Support

For technical support or questions about integration:
- **Documentation**: This API.md file
- **Live API**: https://follow-up-question-f00b29aae45c.herokuapp.com/
- **GitHub Repository**: https://github.com/halderavik/followup_ques_AI

## 🚀 Getting Started Checklist

- [ ] Test the health endpoint: `GET /health`
- [ ] Review available question types: `GET /question-types`
- [ ] Test with a sample request: `POST /generate-followup`
- [ ] Test single reason question: `POST /generate-reason`
- [ ] Choose your integration method (JavaScript, webhooks, etc.)
- [ ] Implement error handling
- [ ] Test with real survey data
- [ ] Deploy to production

---

**Happy surveying! 🎯** 