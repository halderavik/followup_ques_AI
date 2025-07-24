# 🚀 Heroku Deployment Guide

## Prerequisites

Before deploying to Heroku, you need:

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Already set up in your project

## Deployment Steps

### 1. Login to Heroku CLI
```bash
heroku login
```

### 2. Create Heroku App
```bash
heroku create your-app-name
```
Replace `your-app-name` with your desired app name (must be unique across Heroku)

### 3. Set Environment Variables
```bash
heroku config:set DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 4. Deploy to Heroku
```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

### 5. Ensure App is Running
```bash
heroku ps:scale web=1
```

### 6. Open Your App
```bash
heroku open
```

## Important Notes

### Environment Variables
- **DEEPSEEK_API_KEY**: Your DeepSeek API key (already set in step 3)
- **PORT**: Automatically set by Heroku
- **Debug Mode**: Disabled for production

### Files Added for Heroku
- `Procfile`: Tells Heroku how to run your app
- `runtime.txt`: Specifies Python version (3.11.7)
- `gunicorn`: Added to requirements.txt for production WSGI server

### API Endpoints After Deployment
Your API will be available at:
- `https://your-app-name.herokuapp.com/` - API information
- `https://your-app-name.herokuapp.com/health` - Health check
- `https://your-app-name.herokuapp.com/question-types` - Available question types
- `https://your-app-name.herokuapp.com/generate-followup` - Generate follow-up questions

## Troubleshooting

### Check Logs
```bash
heroku logs --tail
```

### Restart App
```bash
heroku restart
```

### Check App Status
```bash
heroku ps
```

## Testing After Deployment

1. **Health Check**: Visit `https://your-app-name.herokuapp.com/health`
2. **API Info**: Visit `https://your-app-name.herokuapp.com/`
3. **Generate Questions**: Use Postman or curl to test the main endpoint

### Example cURL Test
```bash
curl -X POST https://your-app-name.herokuapp.com/generate-followup \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is your favorite programming language?",
    "answer": "I love Python because it is easy to learn and has great libraries.",
    "question_types": ["REASON", "EXAMPLE"]
  }'
```

## Cost Considerations

- **Free Tier**: No longer available on Heroku
- **Basic Dyno**: $7/month for basic hosting
- **Hobby Dyno**: $5/month for hobby projects

## Next Steps After Deployment

1. Update your Postman collection with the new Heroku URL
2. Test all endpoints thoroughly
3. Monitor logs for any issues
4. Consider setting up custom domain if needed 