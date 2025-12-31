# 🧠 AI Incident Responder

> *An AI-powered system that automatically analyzes production incidents, summarizes root causes, and suggests remediation — in real time.*

## 🎯 Overview

Modern systems generate thousands of logs, metrics, traces, and alerts. Engineers waste valuable time searching dashboards, reading noisy logs, and correlating signals manually. **AI Incident Responder** solves this by automatically analyzing incidents using AI and providing actionable insights.

## ✨ Features

- **Real-time Alert Processing**: Receives Datadog webhooks and processes incidents automatically
- **Context Collection**: Automatically fetches logs, traces, and metrics from Datadog
- **AI-Powered Analysis**: Uses Google Gemini to analyze incidents and identify root causes
- **Actionable Recommendations**: Provides specific, actionable steps for remediation
- **Slack Integration**: Sends formatted incident reports to Slack channels
- **Modern Dashboard**: Beautiful React frontend for viewing and testing incident analysis

## 🏗️ Architecture

```
Datadog Alert/Webhook
        │
        ▼
FastAPI (Cloud Run)
        │
   Collect context
 (logs, traces, metrics)
        │
        ▼
     Gemini
        │
        ▼
Incident Summary + RCA + Fix
        │
        ▼
Slack / UI / API Response
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Datadog account (optional, for real integrations)
- Google Gemini API key (or use mock mode)
- Slack webhook URL (optional)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   DATADOG_API_KEY=your_datadog_api_key
   DATADOG_APP_KEY=your_datadog_app_key
   GEMINI_API_KEY=your_gemini_api_key
   SLACK_WEBHOOK_URL=your_slack_webhook_url
   ```

5. **Run the backend:**
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## 📡 API Endpoints

### `POST /webhook/datadog`
Receives Datadog alert webhooks and processes incidents automatically.

**Example webhook payload:**
```json
{
  "title": "High Error Rate Detected",
  "text": "Error rate exceeded 5% threshold",
  "alert_status": "triggered",
  "tags": ["service:api-service", "env:production"]
}
```

### `POST /api/analyze`
Manually trigger incident analysis.

**Request body:**
```json
{
  "alert_title": "High Error Rate Detected",
  "alert_message": "Error rate exceeded threshold",
  "service_name": "api-service",
  "alert_tags": ["service:api-service"]
}
```

**Response:**
```json
{
  "status": "success",
  "analysis": {
    "incident_id": "inc_20240101_120000",
    "summary": "High error rate detected...",
    "root_cause": "Database connection pool exhausted...",
    "recent_changes": "Deployment v1.4.2 was deployed...",
    "recommended_actions": [
      "Check database connection pool metrics",
      "Review deployment v1.4.2 changes"
    ],
    "confidence": "high",
    "severity": "high"
  }
}
```

### `GET /api/incidents`
Get list of recent incidents (placeholder for MVP).

### `GET /health`
Health check endpoint.

## 🔧 Configuration

### Datadog Integration

1. Get your API key and Application key from [Datadog API settings](https://app.datadoghq.com/organization-settings/api-keys)
2. Add them to `.env`:
   ```env
   DATADOG_API_KEY=your_api_key
   DATADOG_APP_KEY=your_app_key
   DATADOG_SITE=datadoghq.com  # or your Datadog site
   ```

3. Configure Datadog webhook:
   - Go to Datadog Monitors → Notifications
   - Add a webhook notification
   - URL: `https://your-api-url/webhook/datadog`

### Gemini AI Integration (Google AI Studio)

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Go to https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy your API key
2. Add to `backend/.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-pro
   ```
   
   **Note:** Available models include:
   - `gemini-pro` (default, recommended)
   - `gemini-1.5-pro` (more capable)
   - `gemini-1.5-flash` (faster, cheaper)

**Note:** The system works in mock mode if API keys are not configured, perfect for demos!

### Slack Integration

1. Create a Slack webhook:
   - Go to [Slack Apps](https://api.slack.com/apps)
   - Create a new app → Incoming Webhooks
   - Add webhook to your channel
2. Add to `.env`:
   ```env
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

## 🎨 Demo Flow

1. **Start the backend and frontend**
2. **Open the dashboard** at `http://localhost:3000`
3. **Test an incident:**
   - Fill in the test form with alert details
   - Click "Analyze Incident"
   - View the AI-generated analysis
4. **Or simulate a Datadog webhook:**
   ```bash
   curl -X POST http://localhost:8000/webhook/datadog \
     -H "Content-Type: application/json" \
     -d '{
       "title": "High Error Rate",
       "text": "Error rate exceeded threshold",
       "alert_status": "triggered",
       "tags": ["service:api-service"]
     }'
   ```

## 🏗️ Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   └── incident.py         # Data models
│   ├── services/
│   │   ├── datadog_service.py   # Datadog API integration
│   │   ├── gemini_service.py    # Gemini AI integration
│   │   └── slack_service.py     # Slack notifications
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🧪 Testing

The system includes mock modes for testing without API keys:

- **Datadog Service**: Returns mock logs, traces, and metrics
- **Gemini Service**: Returns mock analysis responses
- **Slack Service**: Logs messages instead of sending (if not configured)

## 🚢 Deployment

### Google Cloud Run

1. **Build and deploy backend:**
   ```bash
   gcloud run deploy ai-incident-responder \
     --source ./backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

2. **Set environment variables:**
   ```bash
   gcloud run services update ai-incident-responder \
     --set-env-vars DATADOG_API_KEY=xxx,GEMINI_API_KEY=xxx
   ```

3. **Deploy frontend** to Vercel, Netlify, or similar:
   ```bash
   npm run build
   # Deploy dist/ folder
   ```

## 🎯 Key Features Explained

### Prompt Engineering

The system uses carefully crafted prompts to ensure high-quality analysis:

- **Structured Input**: Organizes logs, traces, metrics, and deployments
- **Structured Output**: Requests JSON format with specific fields
- **Context-Aware**: Includes error rates, latency, recent changes
- **Actionable**: Focuses on specific, implementable recommendations

### Context Collection

Automatically fetches:
- **Logs**: Recent error logs from the affected service
- **Traces**: Distributed tracing data showing request flows
- **Metrics**: Error rates, latency (P95), throughput
- **Deployments**: Recent deployment history

## 📝 Development

### Adding New Integrations

1. Create a new service in `backend/services/`
2. Implement the service interface
3. Add to `main.py` dependency injection
4. Update environment variables

### Customizing Prompts

Edit `backend/services/gemini_service.py` → `_build_analysis_prompt()` method.

## 🤝 Contributing

This is a hackathon project! Feel free to:
- Add more monitoring integrations
- Improve prompt engineering
- Add historical incident memory
- Implement feedback loops
- Add voice explanations

## 📄 License

MIT License - feel free to use for your hackathon!

## 🙏 Acknowledgments

- Built for hackathon demo purposes
- Uses Google Gemini for AI analysis
- Integrates with Datadog for monitoring data
- Modern UI built with React and Vite

---

**Built with ❤️ for faster incident response**

