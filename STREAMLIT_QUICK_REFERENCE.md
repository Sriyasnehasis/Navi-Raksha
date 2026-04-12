# Streamlit Quick Reference Guide

## Current Status

✅ **Streamlit is running on port 8501**  
✅ **Backend API is running on port 8000**  
✅ **All systems operational**

---

## Quick Commands

### Start Streamlit

```bash
# Default port (8501)
streamlit run ui/app.py

# Specific port
streamlit run ui/app.py --server.port=8501

# With debug logging
streamlit run ui/app.py --logger.level=debug

# No browser auto-open
streamlit run ui/app.py --server.headless=true
```

### Stop Streamlit

```powershell
# PowerShell - kill all Streamlit processes
Get-Process -Name "*streamlit*" | Stop-Process -Force

# Or with Python
python -c "import os; os.system('taskkill /IM streamlit.exe /F')"
```

### Check Status

```bash
# Test Streamlit response
curl http://localhost:8501

# Test Backend API
curl http://localhost:8000/health

# Check port availability
netstat -ano | findstr :8501
netstat -ano | findstr :8000
```

### View Logs

```bash
# On current terminal (if running in foreground)
# Logs appear directly

# Access Streamlit config
cat ui/.streamlit/config.toml
```

---

## Access Points

| Service                 | URL                          | Purpose                    |
| ----------------------- | ---------------------------- | -------------------------- |
| **Streamlit Frontend**  | http://localhost:8501        | Main EMS dashboard         |
| **Streamlit (Network)** | http://10.5.131.213:8501     | Access from other machines |
| **Backend API**         | http://localhost:8000        | REST API endpoints         |
| **API Health**          | http://localhost:8000/health | System status              |
| **Swagger Docs**        | https://editor.swagger.io/   | API documentation          |

---

## Streamlit Features

### Pages Available

1. **Citizen Tracker** - Emergency request, ambulance tracking
2. **Dispatcher Dashboard** - Control panel, KPIs, dispatch queue
3. **Simulation** - Replay historical scenarios

### Interactive Components

- 🗺️ Folium maps with real-time updates
- 📊 Performance metrics and dashboards
- 🚑 Live ambulance tracking
- 🏥 Hospital bed availability
- ⏱️ ETA predictions with models (RF/LSTM/GNN)
- 📍 A\* routing visualization

---

## Testing Streamlit

### Automated Tests

```bash
# Run comprehensive test
python test_streamlit.py

# Run integration test with backend
python test_streamlit_integration.py
```

### Manual Testing

1. **Open browser:** http://localhost:8501
2. **Click on "Citizen Tracker" page**
3. **Click "REQUEST AMBULANCE" button**
4. **Verify dispatch response with route and hospital rankings**
5. **Check "Dispatcher Dashboard" for KPIs**
6. **Run "Simulation" for historical replay**

---

## Performance Tips

### Improve Load Time

```bash
# Use --client.showErrorDetails=false
streamlit run ui/app.py --client.showErrorDetails=false

# Use --logger.level=warning to reduce logs
streamlit run ui/app.py --logger.level=warning
```

### Optimize for Multiple Users

```bash
# Enable multi-threaded execution
streamlit run ui/app.py --client.toolbarMode=developer
```

### Scale for Production

```bash
# Docker option (see docker setup)
docker build -t navi-raksha-frontend .
docker run -p 8501:8501 navi-raksha-frontend
```

---

## Troubleshooting

| Issue                  | Solution                                                 |
| ---------------------- | -------------------------------------------------------- |
| Port 8501 in use       | `taskkill /IM streamlit.exe /F` then restart             |
| Backend not responding | Start backend: `python modules/backend/app.py`           |
| Empty database         | Seed: `curl -X POST http://localhost:8000/admin/db/seed` |
| Maps not loading       | Install: `pip install folium`                            |
| Slow performance       | Clear cache: delete `.streamlit` folder                  |
| Deprecated warnings    | Update: `pip install --upgrade streamlit`                |

---

## Configuration Files

### Streamlit Config

📄 **Location:** `ui/.streamlit/config.toml`

Keys:

- `[client]` - UI customization
- `[theme]` - Dark/light mode settings
- `[server]` - Port, headless mode
- `[logger]` - Logging verbosity

### Environment Setup

📄 **Location:** `.env` (if using python-dotenv)

Variables:

- `BACKEND_API_URL=http://localhost:8000`
- `STREAMLIT_PORT=8501`
- `DEBUG=False`

---

## File Structure

```
ui/
├── app.py                      # Main entry point
├── citizen_tracker.py          # Tracker page
├── dispatcher_dashboard.py     # Dashboard page
├── simulation.py               # Simulation page
├── .streamlit/
│   └── config.toml            # Streamlit config
└── __pycache__/               # Cache directory
```

---

## Common Errors & Fixes

### Error: "Module not found: streamlit"

```bash
pip install streamlit
```

### Error: "Connection refused localhost:8000"

```bash
# Start backend API first
cd modules/backend
python app.py
```

### Error: "use_container_width deprecated"

**Status:** ⚠️ Just a warning, doesn't break functionality  
**Fix:** Replace `use_container_width=True` with `width='stretch'`

### Error: "No ambulances available"

```bash
# Seed the database
curl -X POST http://localhost:8000/admin/db/seed
```

---

## Key Dependencies

| Package   | Version | Purpose             |
| --------- | ------- | ------------------- |
| streamlit | 1.55.0+ | Frontend framework  |
| requests  | 2.28.0+ | API calls           |
| pandas    | 1.5.0+  | Data handling       |
| numpy     | 1.23.0+ | Numerical computing |
| folium    | 0.14.0+ | Map visualization   |
| plotly    | 5.0.0+  | Interactive charts  |

---

## Deployment Options

### Local Development

```bash
streamlit run ui/app.py --server.port=8501
```

### Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Deploy from your GitHub repo

### Docker

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "ui/app.py"]
```

### Production (with Nginx)

```nginx
location / {
    proxy_pass http://localhost:8501;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## Monitoring & Logging

### Check System Health

```bash
# All components
python test_streamlit_integration.py

# Just Streamlit
python test_streamlit.py

# Just Backend
curl http://localhost:8000/health
```

### View Live Logs

**Streamlit logs appear in the terminal where you ran:**

```
streamlit run ui/app.py
```

### Debug Session

```bash
# Run with debug mode
streamlit run ui/app.py --logger.level=debug

# Monitor resource usage
# Open Task Manager or run: Get-Process python | Select CPU, Memory
```

---

## Useful Links

- 📚 [Streamlit Docs](https://docs.streamlit.io/)
- 🔧 [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- 🐳 [Streamlit Docker Image](https://hub.docker.com/r/streamlit/streamlit)
- 📖 [Folium Maps](https://folium.readthedocs.io/)
- 🌐 [Streamlit Cloud](https://share.streamlit.io/)

---

## Last Updated

**Date:** April 12, 2026  
**Streamlit Version:** 1.55.0  
**Status:** ✅ Operational

---

## Support Channels

- 🐛 Report bugs in GitHub issues
- 💬 Discuss in GitHub discussions
- 📧 Contact: backend-team@navi-raksha.dev
- 📞 Emergency: DevOps hotline

---

**Quick Start:**

```bash
# Terminal 1 - Backend
cd modules/backend && python app.py

# Terminal 2 - Frontend
streamlit run ui/app.py

# Then open browser to: http://localhost:8501
```

✅ **Done! Your EMS platform is live**
