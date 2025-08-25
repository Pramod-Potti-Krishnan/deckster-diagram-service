# 🚨 URGENT: Railway Environment Variables Setup

## Your deployment is failing because environment variables are not configured!

### Quick Fix Steps:

1. **Go to your Railway project dashboard**
2. **Click on your service (deckster-diagram-service)**
3. **Click the "Variables" tab**
4. **Add these variables** (copy and paste each line):

```bash
SUPABASE_URL=https://eshvntffcestlfuofwhv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVzaHZudGZmY2VzdGxmdW9md2h2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1NzkzNDcsImV4cCI6MjA2NzE1NTM0N30.-M1D6lDC4dadS1wZ4-tT-SUf2ZxckvYfUwWl1OeyduA
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVzaHZudGZmY2VzdGxmdW9md2h2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTU3OTM0NywiZXhwIjoyMDY3MTU1MzQ3fQ.7aLWr4fIo1b7T9QH-mHG3Xd00RcqScryPLC1AicZPcY
GOOGLE_API_KEY=AIzaSyBNj49MbCNarOltR_9zpdBIkEsbQlOiO-I
LOGFIRE_TOKEN=pylf_v1_us_82W6vhzxGkTYCHDjDSssVjyDMYnJ1JqjWbMM3b26YcQy
DIAGRAM_BUCKET=diagrams
STORAGE_PUBLIC=true
ENABLE_SEMANTIC_ROUTING=true
GEMINI_MODEL=gemini-2.0-flash-lite
WS_HOST=0.0.0.0
```

5. **Railway will automatically redeploy** after you add the variables

## Visual Guide:

### Step 1: Go to Variables Tab
![Railway Variables Tab](https://docs.railway.app/assets/images/variables-tab.png)

### Step 2: Add Variables
- Click "Add Variable"
- Paste the name (e.g., `SUPABASE_URL`)
- Paste the value
- Repeat for each variable

### Step 3: Save and Deploy
- Railway will automatically redeploy with the new variables

## What Each Variable Does:

- **SUPABASE_URL**: Your Supabase project URL
- **SUPABASE_ANON_KEY**: Public key for Supabase access
- **SUPABASE_SERVICE_KEY**: Admin key for full Supabase access
- **GOOGLE_API_KEY**: For Gemini AI semantic routing
- **LOGFIRE_TOKEN**: For monitoring and logging
- **DIAGRAM_BUCKET**: Storage bucket name
- **STORAGE_PUBLIC**: Makes diagrams publicly accessible
- **ENABLE_SEMANTIC_ROUTING**: Enables AI-powered routing
- **GEMINI_MODEL**: Specific AI model to use
- **WS_HOST**: WebSocket host binding

## After Adding Variables:

The service will:
1. Automatically redeploy
2. Show green checkmarks in logs for configured features
3. Start successfully with all features enabled

## Current Status Without Variables:

```
❌ SUPABASE_URL not configured - storage features disabled
❌ SUPABASE_ANON_KEY not configured - storage features disabled
⚠️ GOOGLE_API_KEY not configured - semantic routing disabled
```

## After Adding Variables:

```
✅ SUPABASE_URL configured
✅ SUPABASE_ANON_KEY configured
✅ GOOGLE_API_KEY configured
```

## Note:
The latest code update allows the service to start without these variables, but features will be limited. For full functionality, add all the variables above.