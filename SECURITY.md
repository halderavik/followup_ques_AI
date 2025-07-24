# 🔐 Security Guide

## API Key Management

### DeepSeek API Key Security

The Survey Intelligence API uses the DeepSeek LLM service for generating follow-up questions. The API key is managed securely to prevent exposure.

#### ✅ Security Measures Implemented

1. **Environment Variables**: API key is stored in `.env` file (not committed to Git)
2. **Git Ignore**: `.env` file is excluded from version control
3. **Server-side Only**: API key is only used server-side, never exposed to clients
4. **No Authentication Required**: End users don't need to provide API keys

#### 🔧 Setup Instructions

1. **Local Development**:
   ```bash
   # Create .env file (not tracked by Git)
   echo "DEEPSEEK_API_KEY=your_actual_api_key_here" > .env
   ```

2. **Heroku Deployment**:
   ```bash
   # Set environment variable securely
   heroku config:set DEEPSEEK_API_KEY=your_actual_api_key_here
   ```

3. **Other Platforms**:
   - Set `DEEPSEEK_API_KEY` as an environment variable
   - Never commit the actual key to version control

#### ⚠️ Security Best Practices

1. **Never commit API keys** to Git repositories
2. **Use environment variables** for all sensitive data
3. **Rotate API keys** regularly
4. **Monitor API usage** for unusual activity
5. **Use HTTPS** for all API communications

#### 🚨 What to Do If API Key is Compromised

1. **Immediately rotate** the DeepSeek API key
2. **Update environment variables** in all deployments
3. **Check for unauthorized usage** in DeepSeek dashboard
4. **Review access logs** for suspicious activity

## API Security Features

### HTTPS Only
- All endpoints use SSL/TLS encryption
- No HTTP traffic allowed

### Input Validation
- All inputs are validated using Pydantic models
- Malicious input is rejected before processing

### CORS Configuration
- Cross-Origin Resource Sharing is enabled
- Allows integration with web-based survey platforms

### Rate Limiting
- Currently no rate limits applied
- Consider implementing if needed for production use

## Data Privacy

### Data Processing
- Survey responses are sent to DeepSeek API for processing
- No data is stored permanently on our servers
- Responses are processed in real-time and discarded

### Logging
- Basic request/response logging for debugging
- No sensitive data is logged
- Logs are not stored permanently

## Compliance

### GDPR Considerations
- No personal data is stored
- Data is processed in real-time only
- Users can request data deletion (though no data is stored)

### Survey Platform Compliance
- Compatible with Qualtrics, SurveyMonkey, and other platforms
- Follows platform-specific security guidelines
- No additional authentication required

## Monitoring and Alerts

### Health Checks
- `/health` endpoint for monitoring
- Automatic health status reporting

### Error Handling
- Comprehensive error responses
- No sensitive information in error messages
- Proper HTTP status codes

## Support and Reporting

### Security Issues
If you discover a security vulnerability:
1. **Do not** create a public GitHub issue
2. **Contact** the development team privately
3. **Provide** detailed information about the issue

### Security Updates
- Regular dependency updates
- Security patches applied promptly
- Monitoring for known vulnerabilities

---

**Remember**: Security is everyone's responsibility. Always follow best practices when handling API keys and sensitive data. 