# Production Deployment Guide - Survey Intelligence API

## Overview

This guide provides step-by-step instructions for deploying the Survey Intelligence API to production, including migrating from DeepSeek LLM to ChatGPT (OpenAI) and deploying to Azure App Service.

## Prerequisites

- Azure subscription
- GitHub account
- Python 3.11+ knowledge
- Basic understanding of Azure services
- OpenAI API key (for ChatGPT integration)

## Phase 1: Code Migration from DeepSeek to ChatGPT

### Step 1: Clone the Repository

```bash
git clone https://github.com/halderavik/followup_ques_AI.git
cd followup_ques_AI
```

### Step 2: Create Production Branch

```bash
git checkout -b production-chatgpt
```

### Step 3: Update Dependencies

Edit `requirements.txt` to include OpenAI SDK:

```txt
Flask==2.3.3
pydantic==2.4.2
requests==2.31.0
python-dotenv==1.1.1
pytest==8.4.1
black==25.1.0
flake8==7.3.0
gunicorn==21.2.0
openai==1.3.0  # Add this line
```

### Step 4: Create ChatGPT Service

Create a new file `app/openai_service.py`:

```python
import os
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from .log_config import setup_logging

class OpenAIAPIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass

class OpenAIService:
    """
    Service class for interacting with OpenAI ChatGPT API.
    """
    TIMEOUT = 25
    RETRIES = 1
    MAX_TOKENS = 80
    CACHE_TTL = 900  # 15 minutes
    
    def __init__(self):
        """Initialize OpenAI service with API key."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.logger = setup_logging()
        self.cache = {}
        self.cache_ttl = self.CACHE_TTL
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for OpenAI API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key for prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                self.logger.info(f"Cache hit for key: {cache_key}")
                return cached_data['response']
            else:
                del self.cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache API response."""
        self.cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        self.logger.info(f"Cached response for key: {cache_key}")
    
    def generate_questions(self, prompt: str) -> Dict[str, Any]:
        """
        Generate follow-up questions using ChatGPT.
        
        Args:
            prompt (str): The prompt for question generation.
            
        Returns:
            Dict[str, Any]: OpenAI API response.
            
        Raises:
            OpenAIAPIError: If the API call fails.
        """
        # Check cache first
        cache_key = self._get_cache_key(prompt)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Track performance
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert survey designer. Generate exactly 3 follow-up questions with these EXACT types: 1) type: 'reason' - ask why, 2) type: 'example' - ask for examples, 3) type: 'impact' - ask about effects. Return ONLY valid JSON with 'followups' array containing 3 objects with 'type' and 'text' fields."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=self.MAX_TOKENS,
                timeout=self.TIMEOUT
            )
            
            # Log performance
            elapsed_time = time.time() - start_time
            self.logger.info(f"OpenAI API call completed in {elapsed_time:.2f}s")
            
            # Cache the response
            self._cache_response(cache_key, response.model_dump())
            
            return response.model_dump()
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise OpenAIAPIError(f"OpenAI API call failed: {e}")
    
    def generate_single_question(self, question: str, response: str, question_type: str) -> str:
        """
        Generate a single follow-up question of specific type.
        
        Args:
            question (str): The original survey question.
            response (str): The user's answer.
            question_type (str): The type of follow-up question.
            
        Returns:
            str: The generated question.
        """
        cache_key = self._get_cache_key(f"{question}:{response}:{question_type}")
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        start_time = time.time()
        
        type_instructions = {
            "reason": "ask why",
            "impact": "ask about effects", 
            "elaboration": "ask for details",
            "example": "ask for examples",
            "clarification": "ask for clarification",
            "comparison": "ask for comparison"
        }
        
        instruction = type_instructions.get(question_type.lower(), "ask a follow-up")
        prompt = f"Question: {question} Answer: {response}. Generate 1 {instruction} question. Return only the question text, no JSON."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"Generate 1 {instruction} question. Return only the question text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=80,
                timeout=self.TIMEOUT
            )
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Single question generation completed in {elapsed_time:.2f}s")
            
            question_text = response.choices[0].message.content.strip()
            self._cache_response(cache_key, question_text)
            
            return question_text
            
        except Exception as e:
            self.logger.error(f"Single question generation error: {e}")
            raise OpenAIAPIError(f"Single question generation failed: {e}")
    
    def cleanup_cache(self):
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, data in self.cache.items()
            if current_time - data['timestamp'] > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
```

### Step 5: Update Routes to Use OpenAI Service

Edit `app/routes.py` to import and use the new service:

```python
# Add this import at the top
from .openai_service import OpenAIService, OpenAIAPIError

# Replace DeepSeekService with OpenAIService in the generate_followup function
def generate_followup():
    """
    Generate follow-up questions for a survey response.
    """
    try:
        data = request.get_json()
        req = GenerateFollowupRequest(**data)
    except ValidationError as ve:
        return jsonify(ValidationErrorResponse(
            detail="Invalid request data.",
            code="validation_error", 
            errors=ve.errors()
        ).dict()), 422
    except Exception as exc:
        return jsonify(ErrorResponse(
            detail=f"Malformed request: {exc}",
            code="bad_request"
        ).dict()), 400

    service = OpenAIService()  # Changed from DeepSeekService
    prompt = service.build_prompt(req.question, req.response)
    try:
        api_response = service.generate_questions(prompt)
        followups = service.parse_response(api_response)
        response = GenerateFollowupResponse(
            followups=[FollowupQuestion(type=QuestionType(f["type"]), text=f["text"]) for f in followups]
        )
        return jsonify(response.dict()), 200
    except OpenAIAPIError as oae:  # Changed from DeepSeekAPIError
        return jsonify(ErrorResponse(
            detail=str(oae),
            code="openai_error"  # Changed from deepseek_error
        ).dict()), 502
    except Exception as exc:
        return jsonify(ErrorResponse(
            detail=f"Internal server error: {exc}",
            code="internal_error"
        ).dict()), 500
```

### Step 6: Update Environment Variables

Create `.env.production` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Azure Configuration (will be set in Azure)
WEBSITES_PORT=5000
```

### Step 7: Update Azure Configuration Files

Create `azure-deploy.yml` for GitHub Actions:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ production-chatgpt ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'your-azure-app-name'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        package: .
```

## Phase 2: Azure Deployment

### Step 8: Azure Resource Setup

#### 8.1 Create Azure App Service

```bash
# Login to Azure CLI
az login

# Create resource group
az group create --name survey-intelligence-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name survey-intelligence-plan \
  --resource-group survey-intelligence-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --name your-survey-intelligence-app \
  --resource-group survey-intelligence-rg \
  --plan survey-intelligence-plan \
  --runtime "PYTHON|3.11"
```

#### 8.2 Configure Environment Variables

```bash
# Set OpenAI API key
az webapp config appsettings set \
  --name your-survey-intelligence-app \
  --resource-group survey-intelligence-rg \
  --settings OPENAI_API_KEY="your_openai_api_key_here"

# Set Flask environment
az webapp config appsettings set \
  --name your-survey-intelligence-app \
  --resource-group survey-intelligence-rg \
  --settings FLASK_ENV="production"

# Set port
az webapp config appsettings set \
  --name your-survey-intelligence-app \
  --resource-group survey-intelligence-rg \
  --settings WEBSITES_PORT="5000"
```

### Step 9: Create Azure Deployment Files

#### 9.1 Create `startup.txt` for Azure

```txt
gunicorn --bind=0.0.0.0 --timeout 600 main:app
```

#### 9.2 Update `requirements.txt` for Azure

```txt
Flask==2.3.3
pydantic==2.4.2
requests==2.31.0
python-dotenv==1.1.1
pytest==8.4.1
black==25.1.0
flake8==7.3.0
gunicorn==21.2.0
openai==1.3.0
```

### Step 10: Deploy to Azure

#### 10.1 Using Azure CLI

```bash
# Navigate to project directory
cd followup_ques_AI

# Deploy using Azure CLI
az webapp deployment source config-local-git \
  --name your-survey-intelligence-app \
  --resource-group survey-intelligence-rg

# Get deployment URL
az webapp deployment list-publishing-credentials \
  --name your-survey-intelligence-app \
  --resource-group survey-intelligence-rg

# Add Azure remote
git remote add azure https://your-username@your-app.scm.azurewebsites.net/your-app.git

# Deploy
git push azure production-chatgpt:master
```

#### 10.2 Using GitHub Actions (Recommended)

1. **Set up GitHub Secrets**:
   - Go to your GitHub repository
   - Navigate to Settings > Secrets and variables > Actions
   - Add `AZURE_WEBAPP_PUBLISH_PROFILE` with your Azure publish profile

2. **Push to trigger deployment**:
```bash
git add .
git commit -m "Add Azure deployment configuration"
git push origin production-chatgpt
```

## Phase 3: Testing and Validation

### Step 11: Test the Deployed Application

#### 11.1 Health Check

```bash
curl https://your-survey-intelligence-app.azurewebsites.net/health
```

Expected response:
```json
{"status": "ok"}
```

#### 11.2 Test Question Generation

```bash
curl -X POST https://your-survey-intelligence-app.azurewebsites.net/generate-followup \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What do you think about our service?",
    "response": "The service is good but could be faster."
  }'
```

Expected response:
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
      "text": "How does the speed impact your overall experience?",
      "type": "impact"
    }
  ]
}
```

### Step 12: Monitor and Optimize

#### 12.1 Set up Azure Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app survey-intelligence-insights \
  --location eastus \
  --resource-group survey-intelligence-rg \
  --application-type web

# Get instrumentation key
az monitor app-insights component show \
  --app survey-intelligence-insights \
  --resource-group survey-intelligence-rg \
  --query instrumentationKey
```

#### 12.2 Configure Monitoring

Add to `requirements.txt`:
```txt
opencensus-ext-azure==1.1.8
```

Update `main.py`:
```python
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

# Configure Azure Application Insights
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=your-key-here'
))
```

## Phase 4: Production Optimization

### Step 13: Performance Optimization

#### 13.1 Enable Azure CDN

```bash
# Create CDN profile
az cdn profile create \
  --name survey-intelligence-cdn \
  --resource-group survey-intelligence-rg \
  --sku Standard_Microsoft

# Create CDN endpoint
az cdn endpoint create \
  --name your-cdn-endpoint \
  --profile-name survey-intelligence-cdn \
  --resource-group survey-intelligence-rg \
  --origin your-survey-intelligence-app.azurewebsites.net \
  --origin-host-header your-survey-intelligence-app.azurewebsites.net
```

#### 13.2 Configure Auto-scaling

```bash
# Enable auto-scaling
az monitor autoscale create \
  --resource-group survey-intelligence-rg \
  --resource your-survey-intelligence-app \
  --resource-type Microsoft.Web/sites \
  --name survey-intelligence-autoscale \
  --min-count 1 \
  --max-count 10 \
  --count 1
```

### Step 14: Security Hardening

#### 14.1 Enable HTTPS

```bash
# Configure SSL binding
az webapp config ssl bind \
  --certificate-thumbprint your-cert-thumbprint \
  --ssl-type SNI \
  --name your-survey-intelligence-app \
  --resource-group survey-intelligence-rg
```

#### 14.2 Set up Azure Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name survey-intelligence-kv \
  --resource-group survey-intelligence-rg \
  --location eastus

# Store OpenAI API key
az keyvault secret set \
  --vault-name survey-intelligence-kv \
  --name OpenAIAPIKey \
  --value "your-openai-api-key"

# Configure web app to use Key Vault
az webapp config appsettings set \
  --name your-survey-intelligence-app \
  --resource-group survey-intelligence-rg \
  --settings @azure/keyvault-secrets
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Issues**:
   - Verify API key is correct
   - Check billing status
   - Ensure proper permissions

2. **Azure Deployment Issues**:
   - Check Azure App Service logs
   - Verify environment variables
   - Check Python version compatibility

3. **Performance Issues**:
   - Monitor Azure Application Insights
   - Check cache hit rates
   - Optimize prompt length

### Support Resources

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)

## Cost Estimation

### Azure Costs (Monthly)
- **App Service Plan (B1)**: ~$13/month
- **Application Insights**: ~$3/month
- **CDN**: ~$5/month
- **Total**: ~$21/month

### OpenAI Costs
- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **Estimated monthly**: $10-50 (depending on usage)

## Next Steps

1. **Set up monitoring alerts**
2. **Implement rate limiting**
3. **Add authentication if needed**
4. **Set up backup and disaster recovery**
5. **Plan for scaling as usage grows**

---

**Note**: This guide assumes you have basic familiarity with Azure services. For more detailed Azure-specific guidance, refer to the official Azure documentation.