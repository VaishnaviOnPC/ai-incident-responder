# Quick Setup Guide

## 🚀 Getting Started in 5 Minutes

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys (optional - works in mock mode)
python -m uvicorn main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Test It!

1. Open http://localhost:3000
2. Fill in the test form
3. Click "Analyze Incident"
4. See the AI analysis!

## 🔑 API Keys (Optional)

The system works in **mock mode** without API keys, perfect for demos!

### To enable real integrations:

1. **Gemini API Key** (for AI analysis):
   - Get from: https://aistudio.google.com/app/apikey
   - Add to `backend/.env`: `GEMINI_API_KEY=your_key`

2. **Datadog** (for real monitoring data):
   - Get from: https://app.datadoghq.com/organization-settings/api-keys
   - Add to `backend/.env`: `DATADOG_API_KEY=xxx` and `DATADOG_APP_KEY=xxx`

3. **Slack** (for notifications):
   - Create webhook: https://api.slack.com/apps
   - Add to `backend/.env`: `SLACK_WEBHOOK_URL=xxx`

## 🎯 Demo Tips

- Use the test form to simulate incidents
- The system provides realistic mock data if APIs aren't configured
- Perfect for hackathon demos!


