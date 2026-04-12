# 🚀 DEPLOYMENT GUIDE - Streamlit Cloud + Render

## PHASE 1: Prepare Code (5 minutes)

### Option A: Deploy from TEST branch (Recommended)

```bash
cd c:\Users\sriya\Desktop\Learner\navi-raksha

# Push test branch with latest code
git push origin test

# Create main branch from test (if needed)
git checkout -b main origin/test
git push -u origin main
```

### Option B: Merge TEST into MAIN

```bash
# If you want main branch updated too
git checkout main
git merge test
git push origin main
```

✅ **Code is ready** - All commits pushed to GitHub

---

## PHASE 2: Deploy Backend to Render (10 minutes)

### Step 1: Go to Render Dashboard

```
https://render.com
```

### Step 2: Connect GitHub Account

- Click "Sign up with GitHub"
- Authorize Render to access your repos
- Allow access to navi-raksha

### Step 3: Create New Web Service

```
Click: "New +" → "Web Service"
```

### Step 4: Configure Backend Service

```
Repository:        navi-raksha
Branch:            main (or test)
Root Directory:    ./modules/backend
Build Command:     pip install -r ../../requirements.txt && python app.py
Start Command:     python app.py
Environment:       Add below
```

### Step 5: Set Environment Variables

```
In Render dashboard → Environment:

FLASK_ENV=production
DATABASE_URL=sqlite:///navi_raksha.db
PORT=8000
```

### Step 6: Deploy & Get URL

```
Click "Deploy"
Wait 2-3 minutes for deployment
Copy your backend URL: https://backend-xxxxx.onrender.com
```

✅ **Backend is LIVE!**

Example response:

```bash
curl https://backend-xxxxx.onrender.com/health
# Returns: {"status": "healthy", "model_loaded": true, ...}
```

---

## PHASE 3: Prepare Frontend for Streamlit Cloud (5 minutes)

### Create secrets file for local testing

```bash
cd c:\Users\sriya\Desktop\Learner\navi-raksha

# Create .streamlit directory if missing
mkdir -p ui/.streamlit

# Create secrets.toml
cat > ui/.streamlit/secrets.toml << EOF
[backend]
API_URL = "https://backend-xxxxx.onrender.com"

[database]
DATABASE_URL = "sqlite:///navi_raksha.db"
EOF
```

### Update ui/app.py to use secrets

At the top of `ui/app.py`, ensure this code exists:

```python
import streamlit as st
import os

# Get backend URL from secrets or environment
try:
    BACKEND_URL = st.secrets["backend"]["API_URL"]
except:
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
```

### Commit changes

```bash
git add -A
git commit -m "Setup: Add Streamlit Cloud secrets configuration"
git push origin main
# or: git push origin test
```

---

## PHASE 4: Deploy Frontend to Streamlit Cloud (10 minutes)

### Step 1: Go to Streamlit Cloud

```
https://share.streamlit.io/
```

### Step 2: Sign In with GitHub

- Click "Sign in with GitHub"
- Authorize Streamlit Cloud

### Step 3: Deploy New App

```
Click: "New app" button
```

### Step 4: Select Repository

```
GitHub Repository: YOUR_USERNAME/navi-raksha
Branch:            main (or test)
Main file path:    ui/app.py
```

### Step 5: Deploy

```
Click "Deploy!"
Wait 2-3 minutes for deployment
Your app URL: https://share.streamlit.io/YOUR_USERNAME/navi-raksha
```

### Step 6: Add Backend URL as Secret

```
1. In your Streamlit Cloud dashboard
2. Click your app → ⚙️ (Settings)
3. Go to "Secrets"
4. Paste:
   [backend]
   API_URL = "https://backend-xxxxx.onrender.com"
5. Save

App auto-redeploys with secret!
```

✅ **Frontend is LIVE!**

---

## FINAL RESULT

After deployment, you'll have:

```
🌐 Frontend (Streamlit Cloud)
   https://share.streamlit.io/YOUR_USERNAME/navi-raksha

🔌 Backend (Render)
   https://backend-xxxxx.onrender.com

✅ Health Check:
   curl https://backend-xxxxx.onrender.com/health

✅ Apps:
   Frontend ←→ Backend (via API calls)
```

---

## QUICK REFERENCE

### Streamlit Cloud URLs

- Dashboard: https://share.streamlit.io/
- My Apps: https://share.streamlit.io/account/apps
- Settings: Account → Settings → Secrets

### Render URLs

- Dashboard: https://render.com/dashboard
- Services: https://render.com/dashboard/services
- Logs: Select service → Logs tab

### Common Tasks

**Redeploy frontend:**

```bash
git push origin main  # Auto-triggers Streamlit redeploy
```

**Redeploy backend:**

```bash
git push origin main  # Auto-triggers Render redeploy
```

**View frontend logs:**

```
Streamlit Cloud dashboard → Select app → "Logs"
```

**View backend logs:**

```
Render dashboard → Select service → "Logs"
```

**Update backend URL in frontend:**

```
Streamlit Cloud → App settings → Secrets → Update BACKEND_URL → Save
```

---

## TROUBLESHOOTING

| Issue                       | Solution                                     |
| --------------------------- | -------------------------------------------- |
| "Cannot connect to backend" | Check BACKEND_URL in Streamlit secrets       |
| "Backend spinning down"     | Render free tier sleeps after 15min (normal) |
| "Import error: modules"     | Ensure requirements.txt in root              |
| "Database not found"        | SQLite works in Cloud (stored in app)        |
| "Slow loading"              | Render free tier may be slow, check logs     |

---

## ESTIMATED TIMELINE

```
5 min:   Push code to GitHub ✅
10 min:  Deploy backend to Render
10 min:  Deploy frontend to Streamlit Cloud
5 min:   Add backend URL to Streamlit secrets
3 min:   Test live apps

TOTAL: ~33 minutes
COST: $0
RESULT: Live EMS system! 🎉
```

---

## DEPLOYMENT COMMANDS (Copy/Paste)

### Push to GitHub

```bash
cd c:\Users\sriya\Desktop\Learner\navi-raksha
git push origin test
git push origin main
```

### Test backend is live

```bash
# After Render deployment
curl https://backend-xxxxx.onrender.com/health
curl https://backend-xxxxx.onrender.com/ambulances/active
```

### Test frontend is live

```
Open: https://share.streamlit.io/YOUR_USERNAME/navi-raksha
Click "Citizen Tracker"
Click "REQUEST AMBULANCE"
Should see dispatch from backend! ✅
```

---

## NEXT STEPS

1. ✅ Push code: `git push origin main`
2. ✅ Deploy backend on Render (connect GitHub, select service)
3. ✅ Deploy frontend on Streamlit Cloud (connect GitHub, select app)
4. ✅ Add backend URL to Streamlit secrets
5. ✅ Test live application
6. ✅ Share URLs with team

---

**Ready to deploy?** Follow the steps above! 🚀

Need help with any step? Let me know!
