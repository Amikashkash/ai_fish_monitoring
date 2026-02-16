# Fish Monitoring System - Complete Setup Guide

This guide will walk you through setting up the entire Fish Monitoring System from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Supabase Database Setup](#supabase-database-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [n8n Automation Setup](#n8n-automation-setup)
6. [Testing the System](#testing-the-system)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Python 3.10 or higher** - [Download](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

### Required Accounts

- **Supabase Account** - [Sign up free](https://supabase.com)
- **Anthropic Account** - [Get API key](https://console.anthropic.com/)

### Optional

- **WhatsApp Business Account** OR **Telegram Bot** - for notifications

## Supabase Database Setup

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Fill in:
   - Project name: `fish-monitoring`
   - Database password: Choose a strong password (save this!)
   - Region: Choose closest to you
4. Click "Create new project"
5. Wait 2-3 minutes for setup to complete

### Step 2: Get Supabase Credentials

1. In your Supabase project dashboard
2. Go to Settings → API
3. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)
4. Save these for later use

### Step 3: Run Database Migration

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New query"
3. Open `C:\Projects\fish-monitoring\supabase\migrations\001_initial_schema.sql`
4. Copy entire content
5. Paste into SQL Editor
6. Click "Run" (or press Ctrl+Enter)
7. You should see success message: "Migration complete!"

### Step 4: Verify Database

1. Go to **Table Editor** in Supabase
2. You should see 7 tables:
   - shipments
   - drug_protocols
   - treatments
   - treatment_drugs
   - daily_observations
   - followup_assessments
   - ai_knowledge
3. Click on `drug_protocols` table
4. You should see 5 pre-loaded medications

✅ **Database setup complete!**

## Backend Setup

### Step 1: Navigate to Backend

```bash
cd C:\Projects\fish-monitoring\backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your command prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI
- Uvicorn
- SQLAlchemy
- Anthropic SDK
- Supabase client
- And more...

Wait for installation to complete (2-3 minutes).

### Step 4: Configure Environment

1. Copy template:
   ```bash
   copy .env.template .env
   ```

2. Open `.env` in text editor

3. Fill in your credentials:
   ```env
   ANTHROPIC_API_KEY=sk-ant-xxxxx  # From Anthropic console
   SUPABASE_URL=https://xxxxx.supabase.co  # From Supabase
   SUPABASE_KEY=eyJxxxxx  # From Supabase
   N8N_WEBHOOK_URL=http://localhost:5678/webhook/fish-monitoring
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ENVIRONMENT=development
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

4. Save the file

### Step 5: Update Database Connection

**Important**: You need to update the database connection string in `app/config/database.py`

1. Open `backend/app/config/database.py`
2. Find the line: `DATABASE_URL = ...`
3. Replace `[YOUR-PASSWORD]` with your actual Supabase password
4. The URL should look like:
   ```python
   DATABASE_URL = (
       f"postgresql://postgres:YOUR_PASSWORD@"
       f"db.{settings.SUPABASE_URL.split('//')[1].split('.')[0]}"
       f".supabase.co:5432/postgres"
   )
   ```

### Step 6: Test Backend

```bash
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Test API:**
1. Open browser
2. Go to `http://localhost:8000/docs`
3. You should see FastAPI interactive documentation

✅ **Backend is running!**

Leave this terminal window open.

## Frontend Setup

### Step 1: Open New Terminal

Open a NEW terminal window (keep backend running in the first one).

### Step 2: Navigate to Frontend

```bash
cd C:\Projects\fish-monitoring\frontend
```

### Step 3: Install Dependencies

```bash
npm install
```

Wait for installation (2-3 minutes).

### Step 4: Configure Environment

1. Copy template:
   ```bash
   copy .env.template .env
   ```

2. Open `.env` in text editor

3. Fill in:
   ```env
   VITE_API_URL=http://localhost:8000
   VITE_SUPABASE_URL=https://xxxxx.supabase.co
   VITE_SUPABASE_ANON_KEY=eyJxxxxx
   ```

4. Save the file

### Step 5: Run Frontend

```bash
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Test PWA:**
1. Open browser
2. Go to `http://localhost:5173`
3. You should see the Fish Monitoring PWA dashboard

✅ **Frontend is running!**

### Step 6: Test Mobile

1. Find your computer's IP address:
   **Windows:**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. On your phone, open browser
3. Go to `http://YOUR_IP:5173`
   (e.g., `http://192.168.1.100:5173`)
4. You should see the PWA on your phone

## n8n Automation Setup

### Step 1: Install n8n

```bash
npm install n8n -g
```

### Step 2: Start n8n

```bash
n8n start
```

**Expected output:**
```
Editor is now accessible via:
http://localhost:5678/
```

### Step 3: Create Account

1. Open `http://localhost:5678` in browser
2. Create your n8n account
3. Choose a username and password

### Step 4: Import Workflows

1. Click "Workflows" in sidebar
2. Click "Import from File"
3. Navigate to `C:\Projects\fish-monitoring\n8n_workflows\`
4. Import each workflow JSON file

### Step 5: Configure Workflows

**For each workflow:**
1. Open the workflow
2. Update API URL nodes:
   - Change to `http://localhost:8000`
3. Configure WhatsApp node (if using):
   - Add WhatsApp Business credentials
   - OR use Telegram as alternative
4. Click "Save"
5. Click "Activate"

✅ **n8n is configured!**

## Testing the System

### End-to-End Test

1. **Create a Shipment**:
   - Open PWA: `http://localhost:5173`
   - Click "Add New Shipment"
   - Fill in:
     - Scientific name: Betta splendens
     - Common name: Siamese Fighting Fish
     - Source: Thailand
     - Quantity: 50
     - Volume: 200
   - Click "Save"

2. **Get AI Recommendation**:
   - Click "Get AI Recommendation"
   - Should say "No historical data" (first time)
   - This is correct!

3. **Start Treatment**:
   - Click "Start Treatment"
   - Select drugs to use
   - Set dosages
   - Click "Begin Treatment"

4. **Daily Observation**:
   - Go to Dashboard
   - Click "Daily Checklist"
   - Rate condition (1-5)
   - Check symptoms
   - Click "Save Observation"

5. **Check Database**:
   - Go to Supabase Table Editor
   - Check `shipments` table - should have 1 row
   - Check `treatments` table - should have 1 row
   - Check `daily_observations` table - should have 1 row

6. **Test API**:
   - Go to `http://localhost:8000/docs`
   - Try GET `/api/shipments`
   - Should return your shipment

✅ **System is working end-to-end!**

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Make sure virtual environment is activated: `venv\Scripts\activate`

**Issue**: `OperationalError: could not connect to server`
- **Solution**: Check DATABASE_URL in `database.py` has correct password

**Issue**: `AuthError: Invalid API key`
- **Solution**: Check ANTHROPIC_API_KEY in `.env` is correct

### Frontend Issues

**Issue**: `Failed to fetch` errors
- **Solution**: Make sure backend is running on `http://localhost:8000`

**Issue**: Blank page
- **Solution**: Check browser console (F12) for errors

**Issue**: Can't access from phone
- **Solution**:
  - Check firewall allows port 5173
  - Make sure phone is on same WiFi network
  - Use computer's IP, not `localhost`

### Database Issues

**Issue**: Migration fails with syntax error
- **Solution**: Make sure you copied ENTIRE SQL file content

**Issue**: Tables not appearing
- **Solution**: Refresh Table Editor page, check Supabase project is active

### n8n Issues

**Issue**: n8n won't start
- **Solution**:
  - Close any process using port 5678
  - Try different port: `n8n start --port 5679`

**Issue**: Workflows not triggering
- **Solution**: Make sure workflow is "Activated" (toggle in top right)

## Next Steps

1. **Add more shipments** to build historical data
2. **Complete treatments** and 5-day follow-ups
3. **Watch AI learn** as you add more data
4. **Deploy to production** (see DEPLOYMENT.md)
5. **Configure WhatsApp** for real notifications

## Getting Help

- Check [README.md](../README.md) for overview
- See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Open issue on GitHub for bugs

---

Need more help? Create an issue with:
- What you're trying to do
- What error you're seeing
- Your environment (Windows/Mac, Python version, etc.)
