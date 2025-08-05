# 🚀 Setup Guide

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Git
- OpenAI API key (get from [OpenAI](https://platform.openai.com/))

### 1. Clone Repository
```bash
git clone https://github.com/halderavik/followup_ques_AI.git
cd followup_ques_AI
```

### 2. Create Virtual Environment
```bash
# Windows
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```bash
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

**🔐 Security**: Never commit your actual API key to Git!

### 5. Run the Application
```bash
python main.py
```

### 6. Test the API
```bash
# Health check
curl http://localhost:5000/health

# Generate follow-up questions
curl -X POST http://localhost:5000/generate-followup \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What challenges do you face at work?",
    "response": "I struggle with time management and communication."
  }'

# Test enhanced multilingual with informativeness detection
curl -X POST http://localhost:5000/generate-enhanced-multilingual \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What challenges do you face at work?",
    "response": "I don't know",
    "type": "reason",
    "language": "English"
  }'
```

**Expected Response (Basic):**
```json
{
  "followups": [
    {
      "text": "Why do you think time management and communication are challenging?",
      "type": "reason"
    },
    {
      "text": "Can you give examples of when these challenges arise?",
      "type": "example"
    },
    {
      "text": "How do these challenges impact your work performance?",
      "type": "impact"
    }
  ]
}
```

**Expected Response (Enhanced Multilingual - Non-informative):**
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

## 🔐 Security Configuration

### API Key Management
1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly** for security
4. **Monitor usage** for unusual activity

### Environment Variables
```bash
# Required
DEEPSEEK_API_KEY=your_actual_api_key_here

# Optional (for production)
FLASK_ENV=production
FLASK_DEBUG=False
```

### Git Security
The following files are automatically ignored:
- `.env` - Environment variables
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `*.log` - Log files

## 🧪 Testing

### Run Tests
```bash
# Using custom test runner (recommended)
python run_tests.py

# Using pytest (if available)
pytest tests/
```

### Test Coverage
- DeepSeek service integration
- API endpoint validation
- Error handling
- Input validation

## 🚀 Deployment

### Heroku Deployment
1. **Install Heroku CLI**
2. **Login to Heroku**
3. **Create app**: `heroku create your-app-name`
4. **Set environment variables**:
   ```bash
   heroku config:set DEEPSEEK_API_KEY=your_actual_api_key_here
   ```
5. **Deploy**: `git push heroku main`

### Other Platforms
- **Railway**: Connect GitHub repository
- **Render**: Deploy from Git
- **AWS**: Use Elastic Beanstalk
- **Google Cloud**: Use App Engine

## 📊 Monitoring

### Health Checks
- **Endpoint**: `GET /health`
- **Expected**: `{"status": "healthy", "timestamp": "..."}`

### Logs
```bash
# Local
tail -f app.log

# Heroku
heroku logs --tail
```

### Performance
- **Response time**: 2-5 seconds
- **Uptime**: 99.9%
- **Rate limits**: None currently

## 🔧 Configuration

### Flask Configuration
```python
# Development
app.config['DEBUG'] = True
app.config['TESTING'] = False

# Production
app.config['DEBUG'] = False
app.config['TESTING'] = False
```

### DeepSeek Configuration
```python
# API URL (configured automatically)
API_URL = "https://api.deepseek.com/v1/chat/completions"

# Model settings
MODEL = "deepseek-chat"
TEMPERATURE = 0.7
MAX_TOKENS = 500
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. API Key Not Found
```bash
Error: DEEPSEEK_API_KEY not found in environment
```
**Solution**: Check your `.env` file and ensure it's in the project root.

#### 2. Import Errors
```bash
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Activate virtual environment and install dependencies.

#### 3. Port Already in Use
```bash
Address already in use
```
**Solution**: Change port in `main.py` or kill existing process.

#### 4. DeepSeek API Errors
```bash
502 Bad Gateway
```
**Solution**: Check API key validity and DeepSeek service status.

### Debug Mode
```bash
# Enable debug mode
export FLASK_DEBUG=1
python main.py
```

## 📚 Documentation

### API Documentation
- **API.md** - Complete API reference
- **POSTMAN_TESTING_GUIDE.md** - Testing guide
- **HEROKU_DEPLOYMENT_GUIDE.md** - Deployment guide

### Security Documentation
- **SECURITY.md** - Security best practices
- **API Key Management** - Secure key handling

### Integration Guides
- **Qualtrics Integration** - Survey platform setup
- **SurveyMonkey Integration** - Webhook configuration
- **Custom Integration** - General HTTP integration

## 🆘 Support

### Getting Help
1. **Check documentation** first
2. **Review troubleshooting** section
3. **Check GitHub issues** for known problems
4. **Create new issue** with detailed information

### Contact Information
- **GitHub**: https://github.com/halderavik/followup_ques_AI
- **Live API**: https://follow-up-question-f00b29aae45c.herokuapp.com/
- **Documentation**: See API.md for detailed integration guide

---

**Happy coding! 🎯** 