# 🚀 Survey Intelligence API - Performance Monitor Frontend

A beautiful, real-time performance monitoring dashboard for the Survey Intelligence API.

## 🌐 Live Demo

**Frontend URL**: https://follow-up-question-f00b29aae45c.herokuapp.com/

## ✨ Features

### 📊 Real-Time Performance Metrics
- **Cache Size**: Number of cached responses
- **Cache TTL**: Time-to-live for cached items (in hours)
- **Timeout**: API request timeout (in seconds)
- **Max Tokens**: Maximum tokens for DeepSeek API calls
- **Retries**: Number of retry attempts
- **API Status**: Real-time online/offline status

### 🧪 Interactive API Testing
- **Health Check**: Test API connectivity
- **Generate Reason Questions**: Test single reason-based question generation
- **Generate Followup Questions**: Test multiple followup question generation
- **Caching Test**: Verify cached response performance

### 📝 Activity Logging
- Real-time activity log with timestamps
- Color-coded log entries (info, success, error, warning)
- Auto-scrolling log display
- Clear log functionality

### ⚡ Performance Features
- **Auto-refresh**: Metrics update every 5 seconds
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Beautiful gradient design with smooth animations
- **Real-time Updates**: Live performance monitoring

## 🎯 How to Use

### 1. Access the Dashboard
Open your browser and navigate to:
```
https://follow-up-question-f00b29aae45c.herokuapp.com/
```

### 2. Monitor Performance
- The dashboard automatically loads performance metrics
- Watch the cache size increase as you make API calls
- Monitor API status in real-time
- Toggle auto-refresh on/off as needed

### 3. Test API Endpoints

#### Health Check
- Click "🏥 Test Health" to verify API connectivity
- View the response in the dedicated response area

#### Generate Reason Question
1. Enter a survey question (pre-filled with example)
2. Enter a user response (pre-filled with example)
3. Click "🎯 Generate Reason Question" to test the endpoint
4. Click "⚡ Test Cached Response" to test caching (same request)

#### Generate Followup Questions
1. Enter a survey question and response
2. Click "🔄 Generate Followup Questions" to test multiple question generation
3. View the generated questions in the response area

### 4. Monitor Activity
- Watch the activity log for real-time updates
- See API call results, errors, and performance metrics
- Clear the log anytime with the "🗑️ Clear Log" button

## 🔧 Technical Details

### Frontend Technologies
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **JavaScript (ES6+)**: Async/await for API calls
- **Fetch API**: Modern HTTP requests
- **Responsive Design**: Mobile-first approach

### API Integration
- **Base URL**: `https://follow-up-question-f00b29aae45c.herokuapp.com`
- **Endpoints Tested**:
  - `GET /api/health` - Health check
  - `GET /api/performance` - Performance metrics
  - `POST /api/generate-reason` - Single reason question
  - `POST /api/generate-followup` - Multiple followup questions

### Performance Monitoring
- **Auto-refresh**: 5-second intervals
- **Cache Monitoring**: Real-time cache size tracking
- **Response Time Tracking**: Built into the API
- **Error Handling**: Comprehensive error display

## 🎨 UI Components

### Performance Metrics Cards
- **Hover Effects**: Cards lift on hover
- **Color Coding**: Different colors for different metrics
- **Real-time Updates**: Values update automatically

### Testing Interface
- **Form Validation**: Ensures required fields are filled
- **Response Display**: Formatted JSON responses
- **Button States**: Visual feedback for actions

### Activity Log
- **Color-coded Entries**:
  - 🔵 Blue: Information
  - 🟢 Green: Success
  - 🔴 Red: Error
  - 🟡 Yellow: Warning
- **Auto-scroll**: New entries appear at the bottom
- **Timestamp**: Each entry shows exact time

## 🚀 Performance Benefits

### Caching Visualization
- **Cache Hit Rate**: See how often responses are cached
- **Response Time**: Compare cached vs. non-cached responses
- **Memory Usage**: Monitor cache size growth

### API Performance
- **Connection Pooling**: Reduced connection overhead
- **Optimized Parameters**: Faster token generation
- **Error Recovery**: Smart retry mechanisms

## 📱 Mobile Responsive

The dashboard is fully responsive and works on:
- **Desktop**: Full feature set with side-by-side layout
- **Tablet**: Optimized layout for medium screens
- **Mobile**: Stacked layout for small screens

## 🔍 Troubleshooting

### Common Issues

1. **API Offline**
   - Check if the Heroku app is running
   - Verify the API base URL is correct
   - Check network connectivity

2. **CORS Errors**
   - The API is configured to allow cross-origin requests
   - If issues persist, check browser console for details

3. **Slow Response Times**
   - Monitor the performance metrics
   - Check cache size and TTL settings
   - Verify DeepSeek API connectivity

### Debug Information
- All API calls are logged in the activity log
- Response times are displayed in the log
- Error details are shown with full context

## 🎯 Use Cases

### For Developers
- **API Testing**: Quick endpoint validation
- **Performance Monitoring**: Real-time metrics tracking
- **Debugging**: Detailed activity logging
- **Caching Verification**: Test cache behavior

### For Product Managers
- **API Health**: Monitor service status
- **Performance Trends**: Track response times
- **Usage Patterns**: Understand API usage
- **Quality Assurance**: Verify functionality

### For Operations
- **Uptime Monitoring**: Real-time status checks
- **Performance Alerts**: Monitor for degradation
- **Capacity Planning**: Track cache usage
- **Troubleshooting**: Quick issue identification

## 🔗 Related Documentation

- **API Documentation**: See `API.md` for detailed API specs
- **Deployment Guide**: See `HEROKU_DEPLOYMENT_GUIDE.md`
- **Security Guide**: See `SECURITY.md` for security details
- **Setup Guide**: See `SETUP_GUIDE.md` for installation

---

**🎉 Enjoy monitoring your Survey Intelligence API performance in real-time!** 