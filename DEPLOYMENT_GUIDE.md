# 🚀 Server Deployment Guide

## ✅ Changes Successfully Pushed to GitHub

Your optimized code has been committed and pushed to:
- **Repository:** https://github.com/nishkarshk212/Ruhixmusic.git
- **Commit:** 31a94e0
- **Changes:** 735 insertions, 57 deletions

---

## 📋 Deployment Options

### Option 1: Deploy to Heroku (Recommended)

#### Prerequisites:
- Heroku account
- Heroku CLI installed
- Git installed

#### Steps:

1. **Login to Heroku:**
   ```bash
   heroku login
   ```

2. **Create a new Heroku app:**
   ```bash
   heroku create your-bot-name
   ```

3. **Set up the buildpacks:**
   ```bash
   heroku buildpacks set heroku/python
   ```

4. **Configure environment variables:**
   ```bash
   # Copy from your .env file
   heroku config:set API_ID=33830507
   heroku config:set API_HASH=54e1e0d86c6c2768b65dc945bb2096c7
   heroku config:set BOT_TOKEN=8775908280:AAFJx86a99qNjE6VjVGL44e8PgTpLrHZJ0g
   heroku config:set MONGO_DB_URI="mongodb+srv://group_saver_242:Nishkarsh123@groupsaver.h2szfwc.mongodb.net/?appName=GroupSaver"
   heroku config:set LOGGER_ID=-1003757375746
   heroku config:set OWNER_ID=8791884726
   heroku config:set STRING_SESSION="BQIENmsAJ_9NThknG121QtK83wMwoDYK64ebiI7w5BdJ5uznYouF3d4tYwn1uD6Wfaukl-vJIgC5j-7r5DcPmFsWfnt96aZG1K3yWcTyAvnCdnjrquqbAuLo734d11pslMiHju50BDqLXVPUJm1ewM_NVAhoKeWt-SvkeijHRkeH6BzVfthGR9riP5e3umtwqsEYo26OpjgKMgkbQK56E7Ux8z4CvVyu9YxZrXsiQV63dqgOozP1d6zzj8FtYJymocRYfEuq6FVeIpZWHbKR7fMuDKr4WNz6qSOsiCEQ7ATpr12emlUWssRavufsMgIVosMxbVjPOxGwXgutfOvMSW7EhmSLGAAAAAH_3hotAA"
   
   # Add optional configs
   heroku config:set API_TIMEOUT=30
   heroku config:set REQUEST_TIMEOUT=60
   ```

5. **Deploy to Heroku:**
   ```bash
   git push heroku main
   ```

6. **Scale the worker:**
   ```bash
   heroku ps:scale worker=1
   ```

7. **View logs:**
   ```bash
   heroku logs --tail
   ```

---

### Option 2: Deploy to VPS/Dedicated Server

#### Requirements:
- Ubuntu/Debian server
- Python 3.8+
- Root or sudo access

#### Steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nishkarshk212/Ruhixmusic.git
   cd Ruhixmusic
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Create .env file:**
   ```bash
   nano .env
   ```
   Paste your environment variables from the original `.env` file.

4. **Start the bot:**
   ```bash
   # Using the optimized script
   chmod +x start_optimized.sh
   ./start_optimized.sh
   
   # Or directly
   python3 -m ANNIEMUSIC
   ```

5. **Run as a service (Optional but recommended):**
   
   Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/anniex.service
   ```
   
   Add this content:
   ```ini
   [Unit]
   Description=ANNIEMUSIC Bot Service
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/path/to/Ruhixmusic
   ExecStart=/usr/bin/python3 -m ANNIEMUSIC
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable anniex
   sudo systemctl start anniex
   sudo systemctl status anniex
   ```

---

### Option 3: Deploy to Railway

1. **Go to:** https://railway.app
2. **Click:** "New Project"
3. **Select:** "Deploy from GitHub repo"
4. **Choose:** your repository
5. **Add environment variables** in Railway dashboard
6. **Deploy!**

---

### Option 4: Deploy to Render

1. **Go to:** https://render.com
2. **Create:** New Web Service
3. **Connect:** Your GitHub repository
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `python3 -m ANNIEMUSIC`
6. **Add environment variables**
7. **Deploy!**

---

### Option 5: Deploy using Docker

1. **Build the image:**
   ```bash
   docker build -t anniex-music .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name anniex \
     --env-file .env \
     --restart unless-stopped \
     anniex-music
   ```

3. **View logs:**
   ```bash
   docker logs -f anniex
   ```

---

## 🔧 Post-Deployment Checks

### 1. Verify Bot is Running:
```bash
# Check process
ps aux | grep python

# Check logs
tail -f log.txt
```

### 2. Test Performance:
```bash
# Run diagnostic
./check_performance.py
```

### 3. Monitor Resources:
```bash
# CPU and Memory
top

# Or use htop if installed
htop
```

---

## 📊 MongoDB Configuration

Your new MongoDB URI is configured:
- **Database:** GroupSaver
- **Connection String:** `mongodb+srv://group_saver_242:Nishkarsh123@groupsaver.h2szfwc.mongodb.net/?appName=GroupSaver`

### Verify Connection:
```bash
./check_performance.py
```

Expected output:
```
✓ MongoDB connection
  Latency: <100ms
MongoDB connection is excellent
```

---

## ⚙️ Environment Variables Reference

Copy these from your `.env` file:

```env
API_ID=33830507
API_HASH=54e1e0d86c6c2768b65dc945bb2096c7
BOT_TOKEN=8775908280:AAFJx86a99qNjE6VjVGL44e8PgTpLrHZJ0g
MONGO_DB_URI=mongodb+srv://group_saver_242:Nishkarsh123@groupsaver.h2szfwc.mongodb.net/?appName=GroupSaver
LOGGER_ID=-1003757375746
OWNER_ID=8791884726
STRING_SESSION=BQIENmsAJ_9NThknG121QtK83wMwoDYK64ebiI7w5BdJ5uznYouF3d4tYwn1uD6Wfaukl-vJIgC5j-7r5DcPmFsWfnt96aZG1K3yWcTyAvnCdnjrquqbAuLo734d11pslMiHju50BDqLXVPUJm1ewM_NVAhoKeWt-SvkeijHRkeH6BzVfthGR9riP5e3umtwqsEYo26OpjgKMgkbQK56E7Ux8z4CvVyu9YxZrXsiQV63dqgOozP1d6zzj8FtYJymocRYfEuq6FVeIpZWHbKR7fMuDKr4WNz6qSOsiCEQ7ATpr12emlUWssRavufsMgIVosMxbVjPOxGwXgutfOvMSW7EhmSLGAAAAAH_3hotAA
NEXGENBOTS_API=https://pvtz.nexgenbots.xyz
VIDEO_API_URL=https://pvtz.nexgenbots.xyz

# Optional
API_TIMEOUT=30
REQUEST_TIMEOUT=60
```

---

## 🐛 Troubleshooting

### Bot won't start:
```bash
# Check logs
tail -f log.txt

# Run diagnostic
./check_performance.py

# Check Python version
python3 --version  # Should be 3.8+
```

### High memory usage:
- Reduce assistant clients (use only STRING_SESSION)
- Decrease worker count in bot.py

### Database connection errors:
- Verify MongoDB URI is correct
- Check network connectivity
- Ensure MongoDB Atlas allows your IP

### Slow performance after deployment:
```bash
# Check server resources
top
free -h
df -h

# Test network latency
ping api.telegram.org
speedtest-cli
```

---

## 📈 Monitoring & Maintenance

### Daily Checks:
1. Bot response time
2. Memory usage
3. Database connection latency
4. Error logs

### Weekly Tasks:
1. Update dependencies: `pip install --upgrade -r requirements.txt`
2. Review error logs
3. Clean up old downloads: `rm -rf downloads/*`
4. Check for Git updates

### Monthly:
1. Review performance metrics
2. Update bot code if needed
3. Rotate sensitive credentials
4. Backup database

---

## 🎯 Performance Benchmarks

After deployment, expect:
- **Response Time:** < 2 seconds for commands
- **Memory Usage:** 200-400 MB
- **CPU Usage:** 10-30% idle, 50-80% under load
- **Database Latency:** < 100ms

---

## 📞 Support

If you need help:
1. Check `OPTIMIZATION_SUMMARY.md`
2. Run `./check_performance.py`
3. Review bot logs
4. Contact: https://t.me/Tele_212_bots

---

**Remember:** Always restart the bot after making configuration changes!
