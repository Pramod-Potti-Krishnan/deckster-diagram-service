# Railway Deployment Guide for Diagram Microservice v2

## ⚠️ IMPORTANT: Configuration Files Fixed
The deployment issues have been resolved by removing deprecated Railway configuration files.
Railway now uses automatic detection and dashboard configuration.

## Repository Status ✅
- **Repository URL**: https://github.com/Pramod-Potti-Krishnan/deckster-diagram-service
- **Branch**: main
- **Status**: Fixed and ready for deployment
- **Latest Fix**: Removed railway.json/railway.toml (these were causing initialization errors)

## Step-by-Step Railway Deployment

### 1. Connect GitHub to Railway
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account (if not already done)
5. Select repository: `Pramod-Potti-Krishnan/deckster-diagram-service`
6. Select branch: `main`

### 2. Configure Environment Variables
In the Railway dashboard, go to the Variables tab and add these environment variables:

#### Required Variables:
```bash
# Supabase Configuration (CRITICAL)
SUPABASE_URL=https://eshvntffcestlfuofwhv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVzaHZudGZmY2VzdGxmdW9md2h2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1NzkzNDcsImV4cCI6MjA2NzE1NTM0N30.-M1D6lDC4dadS1wZ4-tT-SUf2ZxckvYfUwWl1OeyduA
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVzaHZudGZmY2VzdGxmdW9md2h2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTU3OTM0NywiZXhwIjoyMDY3MTU1MzQ3fQ.7aLWr4fIo1b7T9QH-mHG3Xd00RcqScryPLC1AicZPcY

# WebSocket Configuration (PORT is auto-provided by Railway)
WS_HOST=0.0.0.0

# Storage
DIAGRAM_BUCKET=diagrams
STORAGE_PUBLIC=true

# Logging
LOG_LEVEL=INFO
LOGFIRE_TOKEN=pylf_v1_us_82W6vhzxGkTYCHDjDSssVjyDMYnJ1JqjWbMM3b26YcQy
LOGFIRE_ENVIRONMENT=production

# AI Services
GOOGLE_API_KEY=AIzaSyBNj49MbCNarOltR_9zpdBIkEsbQlOiO-I
GEMINI_MODEL=gemini-2.0-flash-lite
ENABLE_SEMANTIC_ROUTING=true

# Performance
MAX_WORKERS=4
REQUEST_TIMEOUT=30
MAX_CONNECTIONS=100

# Features
ENABLE_CACHE=true
ENABLE_FALLBACK=true
ENABLE_METRICS=true

# CORS (Update with your frontend URL)
CORS_ORIGINS=*  # Update this with your actual frontend URL
```

### 3. Add Redis Database (Optional but Recommended)
1. In Railway project, click "New"
2. Select "Database" → "Redis"
3. Railway will automatically set `REDIS_URL` environment variable
4. Update `CACHE_TYPE=redis` in your environment variables

### 4. Deploy Configuration
The repository includes:
- ✅ `Dockerfile` for containerized deployment (Railway will auto-detect)
- ✅ Health check endpoint at `/health`
- ✅ Automatic PORT binding (Railway provides this)
- ✅ No config files needed (Railway uses dashboard configuration)

### 5. Verify Deployment
Once deployed, Railway will provide:
- **Service URL**: `https://deckster-diagram-service-production.up.railway.app`
- **WebSocket Endpoint**: `wss://deckster-diagram-service-production.up.railway.app/ws`

### 6. Test the Deployment

#### Health Check:
```bash
curl https://deckster-diagram-service-production.up.railway.app/health
```

#### WebSocket Test:
```javascript
const ws = new WebSocket('wss://deckster-diagram-service-production.up.railway.app/ws?session_id=test&user_id=user1');

ws.onopen = () => {
    console.log('Connected to Railway deployment');
    ws.send(JSON.stringify({
        type: 'diagram_request',
        correlation_id: 'test-001',
        data: {
            diagram_type: 'pyramid_3_level',
            content: 'Test deployment'
        }
    }));
};

ws.onmessage = (event) => {
    console.log('Response:', JSON.parse(event.data));
};
```

### 7. Monitor Deployment
- **Logs**: Available in Railway dashboard under "Deployments"
- **Metrics**: Railway provides CPU, Memory, and Network metrics
- **Logfire**: Check https://logfire-us.pydantic.dev/pramodpotti/deckster for detailed logs

### 8. Custom Domain (Optional)
1. Go to Settings → Domains in Railway
2. Add your custom domain
3. Update DNS records as instructed by Railway

## Troubleshooting

### Common Issues:

1. **Port Binding Error**
   - Ensure using `${{PORT}}` environment variable
   - Railway assigns port dynamically

2. **WebSocket Connection Failed**
   - Check CORS_ORIGINS includes your frontend URL
   - Verify WebSocket URL uses `wss://` protocol

3. **Supabase Connection Failed**
   - Verify Supabase project is active (not paused)
   - Check API keys are correct
   - Ensure RLS policies allow operations

4. **Memory Issues**
   - Adjust `MAX_WORKERS` environment variable
   - Consider upgrading Railway plan for more resources

## Deployment Status Checklist
- [x] Code pushed to GitHub
- [x] Repository public/accessible
- [x] Dockerfile included
- [x] Railway configuration files included
- [ ] Railway project created
- [ ] GitHub repo connected
- [ ] Environment variables configured
- [ ] Redis database added (optional)
- [ ] Deployment triggered
- [ ] Health check passing
- [ ] WebSocket tested
- [ ] Supabase integration verified

## Support
- **Railway Documentation**: https://docs.railway.app
- **Railway Status**: https://status.railway.app
- **GitHub Repository**: https://github.com/Pramod-Potti-Krishnan/deckster-diagram-service

## Next Steps
1. Login to Railway
2. Create new project
3. Connect GitHub repository
4. Configure environment variables
5. Deploy and monitor

The repository is ready and waiting for deployment! 🚀