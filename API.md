# 📊 Survey Intelligence API Documentation

## Overview

The Survey Intelligence API generates intelligent follow-up questions for open-ended survey responses using advanced AI. This API is designed to integrate seamlessly with survey platforms like **Qualtrics**, **SurveyMonkey**, and other survey tools to enhance data collection and respondent engagement.

**Live API URL**: `https://followup-ai-questions-e534ed0185cb.herokuapp.com/`

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
https://followup-ai-questions-e534ed0185cb.herokuapp.com
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
    "generate_multilingual": "/generate-multilingual",
    "generate_enhanced_multilingual": "/generate-enhanced-multilingual",
    "generate_theme_enhanced": "/generate-theme-enhanced"
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

Generates intelligent follow-up questions for survey responses. By default, generates all 6 question types, but you can specify which types to include using the `allowed_types` parameter.

**Request Body:**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management and communication with my team.",
  "allowed_types": ["reason", "example", "impact"]
}
```

**Response (with allowed_types specified):**
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

**Response (without allowed_types - generates all 6 types):**
```json
{
  "followups": [
    {
      "text": "Why do you think time management and communication are challenging for you?",
      "type": "reason"
    },
    {
      "text": "Could you clarify what specific aspects of communication with your team are difficult?",
      "type": "clarification"
    },
    {
      "text": "Can you elaborate on how time management issues manifest in your daily work?",
      "type": "elaboration"
    },
    {
      "text": "Can you give an example of a recent situation where communication with your team was challenging?",
      "type": "example"
    },
    {
      "text": "What impact has poor time management had on your work or team?",
      "type": "impact"
    },
    {
      "text": "How does your current communication with the team compare to previous experiences in other roles?",
      "type": "comparison"
    }
  ]
}
```

**Note:** 
- If `allowed_types` is provided, generates exactly that many questions with the specified types
- If `allowed_types` is not provided, generates all 6 question types: reason, clarification, elaboration, example, impact, and comparison
- The `allowed_types` parameter accepts any combination of the 6 supported question types
- Questions are generated in the order specified in `allowed_types`

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
- And more (any language OpenAI supports)

**Supported Question Types:**
- `reason` - Ask why
- `impact` - Ask about effects
- `elaboration` - Ask for details
- `example` - Ask for examples
- `clarification` - Ask for clarification
- `comparison` - Ask for comparison

### 7. Generate Enhanced Multilingual Question
**POST** `/generate-enhanced-multilingual`

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

**Informativeness Detection:**
The API automatically detects non-informative responses such as:
- "I don't know", "no", "yes", "maybe", "not sure"
- "我不知道", "不知道", "不", "是" (Chinese)
- "分かりません", "いいえ", "はい", "たぶん" (Japanese)
- And similar patterns in other supported languages

When a response is classified as non-informative (`informative: 0`), no follow-up question is generated, saving API calls and improving user experience.

### 🆕 8. Generate Theme-Enhanced Question
**POST** `/generate-theme-enhanced`

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

**Theme Parameters:**
- **1-10 themes allowed**: You can specify between 1 and 10 themes
- **Importance range**: 0-100% for each theme

**Response (Theme Found):**
```json
{
  "informative": 1,
  "question": "Can you give an example of a situation where face-to-face meetings were more effective than digital communication for your team?",
  "explanation": "This question focuses on the theme of 'communication' by asking the user to elaborate on their preference for face-to-face interactions. It follows the 'elaboration' question type by requesting a specific example, which helps deepen understanding of when and why in-person communication is preferred over digital tools like email or Slack.",
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
  "explanation": "This question gently introduces the missing theme of 'communication' by connecting it to the user's stated preference for blue. It invites them to reflect on whether color preferences might extend beyond personal feelings to interpersonal dynamics, thereby addressing the important theme indirectly.",
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

### 🆕 9. Generate Theme-Enhanced Question with Optional Informative Detection
**POST** `/generate-theme-enhanced-optional`

**NEW!** Generates a theme-enhanced multilingual follow-up question with optional informative detection. Users can choose whether to check if the response is informative or skip this detection for faster processing.

**Request Body (Theme Analysis with Informative Detection Enabled):**
```json
{
  "question": "How do you communicate with your team?",
  "response": "I use email and Slack for most communications, but sometimes face-to-face meetings are more effective.",
  "type": "elaboration",
  "language": "English",
  "theme": "Yes",
  "check_informative": true,
  "theme_parameters": {
    "themes": [
      {"name": "communication", "importance": 80},
      {"name": "leadership", "importance": 60},
      {"name": "collaboration", "importance": 70}
    ]
  }
}
```

**Request Body (Theme Analysis with Informative Detection Disabled):**
```json
{
  "question": "How do you communicate with your team?",
  "response": "I use email and Slack for most communications, but sometimes face-to-face meetings are more effective.",
  "type": "elaboration",
  "language": "English",
  "theme": "Yes",
  "check_informative": false,
  "theme_parameters": {
    "themes": [
      {"name": "communication", "importance": 80},
      {"name": "leadership", "importance": 60},
      {"name": "collaboration", "importance": 70}
    ]
  }
}
```

**Request Body (Standard Mode with Informative Detection Disabled):**
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management and communication.",
  "type": "reason",
  "language": "English",
  "theme": "No",
  "check_informative": false
}
```

**Response (Theme Found with Informative Detection Enabled):**
```json
{
  "informative": 1,
  "question": "Can you provide an example of a situation where face-to-face meetings proved to be more effective than using email or Slack?",
  "explanation": "This question focuses on the theme of 'communication' by asking the user to elaborate on their preference for face-to-face interactions...",
  "original_question": "How do you communicate with your team?",
  "original_response": "I use email and Slack for most communications, but sometimes face-to-face meetings are more effective.",
  "type": "elaboration",
  "language": "English",
  "theme": "Yes",
  "check_informative": true,
  "detected_theme": "communication",
  "theme_importance": 80,
  "highest_importance_theme": null
}
```

**Response (Theme Found with Informative Detection Disabled):**
```json
{
  "informative": null,
  "question": "Can you provide an example of a situation where a face-to-face meeting was more effective than using email or Slack?",
  "explanation": "This question directly focuses on the theme of communication by asking for a specific example...",
  "original_question": "How do you communicate with your team?",
  "original_response": "I use email and Slack for most communications, but sometimes face-to-face meetings are more effective.",
  "type": "elaboration",
  "language": "English",
  "theme": "Yes",
  "check_informative": false,
  "detected_theme": "communication",
  "theme_importance": 80,
  "highest_importance_theme": null
}
```

**Response (Non-informative with Informative Detection Enabled):**
```json
{
  "informative": 0,
  "question": null,
  "explanation": null,
  "original_question": "What challenges do you face at work?",
  "original_response": "I don't know",
  "type": "reason",
  "language": "English",
  "theme": "Yes",
  "check_informative": true,
  "detected_theme": null,
  "theme_importance": null,
  "highest_importance_theme": null
}
```

**Response (Non-informative with Informative Detection Disabled):**
```json
{
  "informative": null,
  "question": "Why do you think communication might be a challenge at work, or do you feel it's not an issue for you?",
  "explanation": "This question gently introduces the missing theme of 'communication' by connecting it to the user's response...",
  "original_question": "What challenges do you face at work?",
  "original_response": "I don't know",
  "type": "reason",
  "language": "English",
  "theme": "Yes",
  "check_informative": false,
  "detected_theme": null,
  "theme_importance": null,
  "highest_importance_theme": "communication"
}
```

**Key Features:**
- **Optional Informative Detection**: Set `check_informative` to `true` to enable informative detection, or `false` to skip it for faster processing
- **Performance Optimization**: When `check_informative` is `false`, the API skips the informative detection step, resulting in faster response times
- **Flexible Usage**: Users can choose the level of analysis based on their needs
- **Backward Compatibility**: Maintains all existing theme-enhanced functionality
- **Multilingual Support**: Works with all supported languages

**Use Cases:**
- **High-Volume Processing**: Use `check_informative: false` for batch processing where speed is more important than informative detection
- **Quality Assurance**: Use `check_informative: true` when you need to ensure responses are informative before generating follow-up questions
- **Real-time Applications**: Use `check_informative: false` for real-time chat applications where response speed is critical

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

#### Method 3: Theme-Enhanced Integration
```javascript
// Theme-enhanced integration for employee surveys
Qualtrics.SurveyEngine.addOnload(function() {
    var response = $('QR~QID1').value;
    
    fetch('https://follow-up-question-f00b29aae45c.herokuapp.com/generate-theme-enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question: "How satisfied are you with your work environment?",
            response: response,
            type: "elaboration",
            language: "English",
            theme: "Yes",
            theme_parameters: {
                themes: [
                    {"name": "communication", "importance": 85},
                    {"name": "work_life_balance", "importance": 75},
                    {"name": "teamwork", "importance": 70}
                ]
            }
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.informative === 1) {
            Qualtrics.SurveyEngine.setEmbeddedData('theme_question', data.question);
            Qualtrics.SurveyEngine.setEmbeddedData('detected_theme', data.detected_theme);
            Qualtrics.SurveyEngine.setEmbeddedData('theme_importance', data.theme_importance);
        }
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

#### cURL Example for Theme-Enhanced API
```bash
curl -X POST https://follow-up-question-f00b29aae45c.herokuapp.com/generate-theme-enhanced \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

#### cURL Example with Equal Weights (Random Selection)
```bash
curl -X POST https://follow-up-question-f00b29aae45c.herokuapp.com/generate-theme-enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do you handle conflicts in your team?",
    "response": "I try to listen to all perspectives and find common ground.",
    "type": "impact",
    "language": "English",
    "theme": "Yes",
    "theme_parameters": {
      "themes": [
        {"name": "communication", "importance": 80},
        {"name": "leadership", "importance": 80},
        {"name": "conflict_resolution", "importance": 80}
      ]
    }
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

# Theme-enhanced API example
def generate_theme_enhanced_question(question, response, theme_parameters):
    url = "https://follow-up-question-f00b29aae45c.herokuapp.com/generate-theme-enhanced"
    
    payload = {
        "question": question,
        "response": response,
        "type": "elaboration",
        "language": "English",
        "theme": "Yes",
        "theme_parameters": theme_parameters
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code}")

# Usage example for theme-enhanced API
try:
    theme_params = {
        "themes": [
            {"name": "communication", "importance": 80},
            {"name": "leadership", "importance": 60},
            {"name": "collaboration", "importance": 70}
        ]
    }
    
    result = generate_theme_enhanced_question(
        question="How do you communicate with your team?",
        response="I use email and Slack for most communications, but sometimes face-to-face meetings are more effective.",
        theme_parameters=theme_params
    )
    
    if result['informative'] == 1:
        print(f"Detected theme: {result.get('detected_theme')}")
        print(f"Theme importance: {result.get('theme_importance')}%")
        print(f"Generated question: {result['question']}")
        print(f"Explanation: {result.get('explanation')}")
    else:
        print("Response was not informative enough")
        
except Exception as e:
    print(f"Error: {e}")

# Usage example with equal weights (random selection)
try:
    equal_theme_params = {
        "themes": [
            {"name": "communication", "importance": 80},
            {"name": "leadership", "importance": 80},
            {"name": "conflict_resolution", "importance": 80}
        ]
    }
    
    result = generate_theme_enhanced_question(
        question="How do you handle conflicts in your team?",
        response="I try to listen to all perspectives and find common ground.",
        theme_parameters=equal_theme_params
    )
    
    if result['informative'] == 1:
        print(f"Detected theme: {result.get('detected_theme')}")
        print(f"Highest importance theme: {result.get('highest_importance_theme')}")
        print(f"Generated question: {result['question']}")
        print(f"Explanation: {result.get('explanation')}")
    else:
        print("Response was not informative enough")
        
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

// Theme-enhanced API example
async function generateThemeEnhancedQuestion(question, response, themeParameters) {
    try {
        const result = await axios.post(
            'https://follow-up-question-f00b29aae45c.herokuapp.com/generate-theme-enhanced',
            {
                question: question,
                response: response,
                type: "elaboration",
                language: "English",
                theme: "Yes",
                theme_parameters: themeParameters
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

// Usage example for theme-enhanced API
const themeParams = {
    themes: [
        {name: "communication", importance: 80},
        {name: "leadership", importance: 60},
        {name: "collaboration", importance: 70}
    ]
};

generateThemeEnhancedQuestion(
    "How do you communicate with your team?",
    "I use email and Slack for most communications, but sometimes face-to-face meetings are more effective.",
    themeParams
)
.then(result => {
    if (result.informative === 1) {
        console.log(`Detected theme: ${result.detected_theme}`);
        console.log(`Theme importance: ${result.theme_importance}%`);
        console.log(`Generated question: ${result.question}`);
        console.log(`Explanation: ${result.explanation}`);
    } else {
        console.log("Response was not informative enough");
    }
})
.catch(error => {
    console.error('Error:', error);
});

// Usage example with equal weights (random selection)
const equalThemeParams = {
    themes: [
        {name: "communication", importance: 80},
        {name: "leadership", importance: 80},
        {name: "conflict_resolution", importance: 80}
    ]
};

generateThemeEnhancedQuestion(
    "How do you handle conflicts in your team?",
    "I try to listen to all perspectives and find common ground.",
    equalThemeParams
)
.then(result => {
    if (result.informative === 1) {
        console.log(`Detected theme: ${result.detected_theme}`);
        console.log(`Highest importance theme: ${result.highest_importance_theme}`);
        console.log(`Generated question: ${result.question}`);
        console.log(`Explanation: ${result.explanation}`);
    } else {
        console.log("Response was not informative enough");
    }
})
.catch(error => {
    console.error('Error:', error);
});
```

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
  "response": "The interface is confusing and it's too slow.",
  "allowed_types": ["clarification", "example", "impact"]
}
```

**Generated Follow-ups:**
1. "Could you clarify what specific aspects of the interface you find confusing?"
2. "Can you give specific examples of parts of the interface that you find confusing?"
3. "How does the slowness of the product impact your daily workflow or productivity?"

### Employee Satisfaction Survey
```json
{
  "question": "How satisfied are you with your work environment?",
  "response": "I like my colleagues but the office space is too crowded.",
  "allowed_types": ["reason", "example", "comparison"]
}
```

**Generated Follow-ups:**
1. "Why do you enjoy working with your colleagues?"
2. "Can you give an example of a situation where the crowded office space was problematic?"
3. "How does this work environment compare to your previous workplaces?"

### All 6 Question Types Example
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management and communication with my team."
}
```

**Generated Follow-ups (all 6 types):**
1. "Why do you think time management is a challenge for you?" (reason)
2. "Could you clarify what specific aspects of communication with your team are difficult?" (clarification)
3. "Can you elaborate on how time management issues manifest in your daily work?" (elaboration)
4. "Can you give an example of a recent situation where communication with your team was challenging?" (example)
5. "What impact has poor time management had on your work or team?" (impact)
6. "How does your current communication with the team compare to previous experiences in other roles?" (comparison)

### Single Reason Question Example
```json
{
  "question": "What do you think about our product?",
  "response": "The interface is confusing and it's too slow."
}
```

**Generated Reason Question:**
"Why do you find the interface confusing and slow?"

### Theme-Enhanced Example
```json
{
  "question": "How do you handle team conflicts?",
  "response": "I try to communicate openly and lead by example to foster collaboration.",
  "type": "impact",
  "language": "English",
  "theme": "Yes",
  "theme_parameters": {
    "themes": [
      {"name": "communication", "importance": 80},
      {"name": "leadership", "importance": 90},
      {"name": "collaboration", "importance": 70}
    ]
  }
}
```

**Generated Theme-Enhanced Question:**
"What positive impacts have you observed in your team as a result of your leadership approach to handling conflicts?"

**Theme Analysis:**
- Detected theme: "leadership" (90% importance)
- Generated impact-focused question
- Provided explanation for question generation

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

## 📊 Performance & Response Times

### API Performance Metrics (Updated August 2025)

**Average Response Times:**
- **`/generate-followup`** (with only 'reason' type): **2,394 ms** (~2.4 seconds)
- **`/generate-reason`**: **2,678 ms** (~2.7 seconds)
- **`/generate-multilingual`**: **2,009 ms** (~2.0 seconds)
- **`/generate-enhanced-multilingual`**: **3,215 ms** (~3.2 seconds)
- **`/generate-theme-enhanced`** (standard): **1,795 ms** (~1.8 seconds)
- **`/generate-theme-enhanced`** (theme analysis): **2,278 ms** (~2.3 seconds)

**Performance Insights:**
- **Fastest endpoint**: `/generate-theme-enhanced` (standard mode) at ~1.8 seconds
- **Slowest endpoint**: `/generate-enhanced-multilingual` at ~3.2 seconds
- **Consistent performance**: All endpoints respond within 1.8-3.2 seconds
- **Enhanced features**: Theme analysis and informativeness detection add ~0.5-1.4 seconds

### Rate Limits & Availability
- **No rate limits** currently applied
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
- **Live API**: https://followup-ai-questions-e534ed0185cb.herokuapp.com/
- **GitHub Repository**: https://github.com/halderavik/followup_ques_AI

## 🚀 Getting Started Checklist

- [ ] Test the health endpoint: `GET /health`
- [ ] Review available question types: `GET /question-types`
- [ ] Test with a sample request: `POST /generate-followup`
- [ ] Test single reason question: `POST /generate-reason`
- [ ] Test theme-enhanced API: `POST /generate-theme-enhanced`
- [ ] Choose your integration method (JavaScript, webhooks, etc.)
- [ ] Implement error handling
- [ ] Test with real survey data
- [ ] Deploy to production

---

**Happy surveying! 🎯** 