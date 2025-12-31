# 🧠 AI Incident Responder - Project Summary

## 📋 Overview

**AI Incident Responder** is an AI-powered system that automatically analyzes production incidents, identifies root causes, and suggests remediation steps in real-time. Built for hackathon demonstration.

## 🎯 Core Value Proposition

- **Saves Time**: Reduces mean time to recovery (MTTR) by automatically analyzing incidents
- **AI-Powered**: Uses Google Gemini to understand complex failure chains
- **Real-time**: Processes Datadog alerts instantly
- **Actionable**: Provides specific, implementable recommendations

## 🏗️ Architecture

```
┌─────────────────┐
│  Datadog Alert  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │  ← Webhook receiver
│  (Cloud Run)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context Fetcher │  ← Pulls logs, traces, metrics
│ (Datadog API)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Analyzer    │  ← Gemini AI analysis
│  (Google AI Studio) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Response       │  ← Summary + RCA + Fixes
│  Generator      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Slack  │ │  UI    │
└────────┘ └────────┘
```

## 🔑 Key Components

### 1. Backend (FastAPI)
- **Webhook Listener**: Receives Datadog alerts
- **Context Fetcher**: Pulls logs, traces, metrics from Datadog
- **AI Analyzer**: Uses Gemini to analyze incidents
- **Notifier**: Sends results to Slack

### 2. Frontend (React)
- **Dashboard**: Beautiful UI for viewing incidents
- **Test Interface**: Manual incident testing
- **Real-time Updates**: Shows analysis results

### 3. AI Prompt Engineering
The system uses carefully crafted prompts to ensure quality:
- Structured input (logs, traces, metrics, deployments)
- Structured output (JSON with specific fields)
- Context-aware analysis
- Actionable recommendations

## 📊 Data Flow

1. **Alert Received**: Datadog sends webhook to `/webhook/datadog`
2. **Context Collection**: System fetches:
   - Recent error logs (last 15 minutes)
   - Distributed traces
   - Metrics (error rate, latency)
   - Recent deployments
3. **AI Analysis**: Gemini processes context and generates:
   - Summary
   - Root cause analysis
   - Recent changes identification
   - Recommended actions
   - Confidence level
4. **Response**: Results sent to:
   - Slack (if configured)
   - API response
   - Frontend dashboard

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python) |
| Frontend | React + Vite |
| AI | Google Gemini (Google AI Studio) |
| Monitoring | Datadog |
| Notifications | Slack Webhooks |
| Hosting | Google Cloud Run (backend) |
| Styling | Modern CSS with gradients |

## 🎨 UI Features

- **Modern Design**: Beautiful gradient UI
- **Real-time**: Updates as incidents are processed
- **Test Interface**: Easy incident simulation
- **Responsive**: Works on desktop and mobile
- **Color-coded**: Severity and confidence indicators

## 🔧 Configuration

### Required (for full functionality):
- Google Gemini API key
- Datadog API keys (optional - mock mode available)
- Slack webhook URL (optional)

### Mock Mode:
System works without API keys for demos:
- Mock Datadog data
- Mock AI analysis
- Logged Slack messages

## 📈 Demo Flow

1. **Start Services**: Backend + Frontend
2. **Simulate Alert**: Use test form or send webhook
3. **AI Analysis**: System analyzes incident
4. **View Results**: See summary, root cause, actions
5. **Slack Notification**: (if configured) Message sent to channel

## 🚀 Deployment

### Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Production (Cloud Run)
```bash
gcloud run deploy ai-incident-responder \
  --source ./backend \
  --platform managed \
  --region us-central1
```

## 📝 Key Files

- `backend/main.py`: FastAPI application
- `backend/services/gemini_service.py`: AI analysis logic
- `backend/services/datadog_service.py`: Monitoring integration
- `frontend/src/App.jsx`: Main React component
- `README.md`: Full documentation

## 🎯 Hackathon Highlights

- **Real-time Processing**: Instant incident analysis
- **AI-Powered**: Advanced root cause identification
- **Production-Ready**: Works with real monitoring systems
- **Beautiful UI**: Modern, responsive design
- **Easy Demo**: Works in mock mode without API keys

## 🔮 Future Enhancements

- Historical incident memory
- Feedback loop ("Was this helpful?")
- Auto-create Jira tickets
- Voice explanations (ElevenLabs)
- Multi-service correlation
- Predictive alerts

---

**Built for faster incident response** ⚡

