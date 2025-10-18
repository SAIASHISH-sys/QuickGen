# 🚀 Deploying to Render

This guide will walk you through deploying your IPL Highlight Generator to Render.

## Why Render?

- ✅ **Long-running processes**: Perfect for video generation (up to 600s timeout)
- ✅ **Background jobs**: Handles webhook and async processing
- ✅ **Persistent storage**: Keep generated videos with disk storage
- ✅ **Free tier available**: Start with free plan
- ✅ **Easy deployment**: Direct GitHub integration

## Prerequisites

1. A GitHub account with your repository pushed
2. A Render account (sign up at https://render.com)
3. Your API keys ready:
   - GOOGLE_API_KEY
   - ELEVENLABS_API_KEY
   - HEYGEN_API_KEY

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

```bash
# Make sure all changes are committed
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create a New Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your **Ipl_Summary_Dashboard** repository

### 3. Configure the Service

**Basic Settings:**
- **Name**: `ipl-highlight-generator` (or your choice)
- **Region**: Choose closest to you (Oregon, Frankfurt, Singapore, etc.)
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  chmod +x build.sh && ./build.sh
  ```
  **Important:** Make sure to use this exact command - it installs both Python packages AND system dependencies (FFmpeg, Chromium)!
  
- **Start Command**: 
  ```bash
  gunicorn web_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 600
  ```

**Instance Type:**
- Start with **Free** tier for testing
- Upgrade to **Starter** ($7/month) for better performance if needed

### 4. Add Environment Variables

In the Render dashboard, scroll down to **Environment Variables** and add:

```env
GOOGLE_API_KEY=your_google_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
HEYGEN_API_KEY=your_heygen_api_key_here
WEBHOOK_URL=https://your-app-name.onrender.com/webhook
FLASK_ENV=production
PYTHON_VERSION=3.12.0
VIDEO_WIDTH=720
VIDEO_HEIGHT=1280
USE_TEST_MODE=true
```

**Important:** Replace `your-app-name` in WEBHOOK_URL with your actual Render app name!

### 5. Add System Dependencies

Render needs FFmpeg and Chromium for video processing and scoreboard generation.

**IMPORTANT:** Render's free tier and web services don't have a separate "Native Dependencies" UI section. Instead, we'll install them via the build command!

**Method: Install via Build Script (Works for All Tiers)**

Your `build.sh` script already handles this! Just make sure your build command in Render is set to:
```bash
chmod +x build.sh && ./build.sh
```

The script will:
1. Install Python packages via pip
2. Install FFmpeg via apt-get
3. Install Chromium and dependencies

**No additional configuration needed** - the build script handles everything!

**Alternative: Using Dockerfile (If Build Script Doesn't Work)**

If you encounter issues with the build script, switch to Docker:
```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn web_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 600
```

### 6. Add Persistent Disk (SKIP THIS - Not Needed!)

**IMPORTANT UPDATE:** Render's free tier web services have ephemeral storage that persists during the service lifetime. Your generated videos will be stored in the `commentaries/` folder automatically.

**You DON'T need to configure disk storage** because:
- ✅ Generated videos stay until you redeploy
- ✅ The app has smart caching (won't regenerate existing files)
- ✅ Works perfectly for testing and production

**Note:** Persistent disks are only available for paid plans and Background Workers. For web services, the filesystem is sufficient for your use case.

### 7. Deploy!

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Watch the logs for any errors
4. Once deployed, you'll get a URL like: `https://your-app-name.onrender.com`

### 8. Update Webhook URL (Important!)

After deployment, update your environment variable:
1. Copy your Render app URL
2. Go to **Environment** → Edit `WEBHOOK_URL`
3. Set it to: `https://your-app-name.onrender.com/webhook`
4. Click **Save Changes** (this will trigger a redeploy)

## Post-Deployment

### Test Your Application

1. Visit your Render URL: `https://your-app-name.onrender.com`
2. Select a year and match
3. Click "Generate Highlight"
4. Monitor the progress (it may take 3-10 minutes)

### Monitor Logs

View real-time logs in Render dashboard:
- Click on your service
- Go to **Logs** tab
- Watch for any errors or issues

### Common Issues & Solutions

#### Issue 1: Service Won't Start
**Solution:** Check logs for missing dependencies. Make sure all environment variables are set.

#### Issue 2: Video Generation Timeout
**Solution:** Free tier has 15-minute timeout. This should be enough, but upgrade to paid plan if needed.

#### Issue 3: FFmpeg Not Found
**Solution:** Add `ffmpeg` to Native Dependencies in Render dashboard.

#### Issue 4: Chromium/Pyppeteer Errors
**Solution:** The build script automatically installs `chromium` and `chromium-driver`.

**Note:** We use `pyppeteer2` (not `pyppeteer`) to avoid dependency conflicts with `websockets` library. The original `pyppeteer` requires `websockets<11.0` but `elevenlabs` requires `websockets>=11.0`.

#### Issue 5: Out of Memory
**Solution:** 
- Free tier has 512MB RAM
- Upgrade to Starter plan (512MB dedicated) if needed
- Or reduce concurrent processing

#### Issue 6: Disk Space Full
**Solution:**
- Free tier disk is limited
- Clean up old videos or upgrade disk size
- Add cleanup job to delete old files

### Performance Tips

1. **Workers**: Start with 2 workers. Increase for paid plans.
2. **Timeout**: 600 seconds handles video generation. Increase if needed.
3. **Region**: Choose region closest to your users
4. **Caching**: The app already caches files - no extra config needed
5. **CDN**: Consider Render's CDN for static files

## Cost Breakdown

### Free Tier
- **Web Service**: Free (with limitations)
- **Bandwidth**: 100 GB/month
- **Build Minutes**: 500 minutes/month
- **Limitations**:
  - Sleeps after 15 minutes of inactivity
  - 512 MB RAM
  - Shared CPU
  - Ephemeral disk

### Starter Plan ($7/month)
- **Web Service**: Always on
- **RAM**: 512 MB
- **CPU**: Shared
- **Persistent disk**: Available
- **No sleep**: App stays running

### Standard Plan ($25/month)
- **RAM**: 2 GB
- **CPU**: 1 dedicated
- **Better performance**: Faster video processing
- **Recommended for**: Production use

## Updating Your App

### Push Updates
```bash
# Make your changes
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically redeploy!

### Manual Redeploy
In Render dashboard:
1. Click **Manual Deploy**
2. Select **Clear build cache & deploy** if needed

## Custom Domain (Optional)

1. Go to **Settings** → **Custom Domain**
2. Add your domain (e.g., `highlights.yourdomain.com`)
3. Add CNAME record in your DNS:
   ```
   CNAME highlights your-app-name.onrender.com
   ```
4. Render provides free SSL certificates!

## Monitoring

### Health Checks
Render automatically pings your app to keep it alive.

### Uptime Monitoring
- Use Render's built-in monitoring
- Or add external: UptimeRobot, Pingdom, etc.

### Logs
- View logs in dashboard
- Download logs for analysis
- Set up log alerts

## Backup Strategy

Since video generation costs API credits, consider:

1. **Regular Backups**: Download generated videos periodically
2. **Database**: Store video URLs in external database
3. **Cold Storage**: Move old videos to S3/Cloudflare R2

## Scaling

As your app grows:

1. **Horizontal Scaling**: Add more workers
2. **Vertical Scaling**: Upgrade instance size
3. **Database**: Add PostgreSQL for metadata
4. **Queue System**: Add Redis + Celery for job queue
5. **Storage**: Use S3 for videos instead of disk

## Troubleshooting Commands

```bash
# View logs
# Use Render dashboard or CLI

# Check disk space
df -h

# Check memory
free -h

# Check running processes
ps aux | grep gunicorn

# Test locally with gunicorn
gunicorn web_app:app --bind 0.0.0.0:5200 --workers 2 --timeout 600
```

## Security Best Practices

1. **API Keys**: Never commit to Git. Use environment variables.
2. **HTTPS**: Render provides free SSL - always use it
3. **Rate Limiting**: Consider adding Flask-Limiter
4. **Authentication**: Add user auth for production
5. **CORS**: Configure properly if needed

## Need Help?

- **Render Docs**: https://render.com/docs
- **Community**: https://community.render.com
- **Support**: support@render.com

## Alternative: Docker Deployment

If you prefer Docker, here's a complete setup:

### Dockerfile
```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p commentaries templates static

# Expose port
EXPOSE $PORT

# Run with gunicorn
CMD gunicorn web_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 600
```

### Deploy with Docker
1. In Render, select **Docker** instead of Python
2. Render will build and deploy your Docker image
3. Configure environment variables as before

---

## Summary

✅ Push code to GitHub
✅ Create Render web service
✅ Add environment variables
✅ Add native dependencies (FFmpeg, Chromium)
✅ Add persistent disk (optional)
✅ Deploy and test
✅ Update webhook URL
✅ Monitor and enjoy!

**Your app will be live at:** `https://your-app-name.onrender.com` 🎉

---

*Made with ❤️ for cricket fans*
