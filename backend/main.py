"""
AI Incident Responder - FastAPI Backend
Receives Datadog webhooks and processes incidents using Gemini AI
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from datetime import datetime, timedelta
import logging

import sys
from pathlib import Path
from dotenv import load_dotenv
from db.incidents_repo import save_incident, get_incidents

# Load environment variables
load_dotenv()

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.datadog_service import DatadogService
from services.gemini_service import GeminiService
from services.slack_service import SlackService
from models.incident import IncidentAnalysis, IncidentRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Incident Responder",
    description="AI-powered system for analyzing production incidents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
datadog_service = DatadogService()
gemini_service = GeminiService()
slack_service = SlackService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Incident Responder",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/webhook/datadog")
async def datadog_webhook(request: Request):
    """
    Receives Datadog alert webhooks and processes incidents
    """
    try:
        payload = await request.json()
        logger.info(f"Received Datadog webhook: {payload.get('title', 'Unknown alert')}")
        
        # Extract alert information
        alert_title = payload.get("title", "Unknown Alert")
        alert_message = payload.get("text", "")
        alert_status = payload.get("alert_status", "triggered")
        alert_tags = payload.get("tags", [])
        
        # Only process triggered alerts
        if alert_status != "triggered":
            logger.info(f"Alert status is {alert_status}, skipping analysis")
            return {"status": "skipped", "reason": f"Alert status: {alert_status}"}
        
        # Extract service name from tags or alert
        service_name = None
        for tag in alert_tags:
            if tag.startswith("service:"):
                service_name = tag.split(":")[1]
                break
        
        if not service_name:
            # Try to extract from alert message
            service_name = "unknown_service"
        
        # Create incident request
        incident_request = IncidentRequest(
            alert_title=alert_title,
            alert_message=alert_message,
            service_name=service_name,
            alert_tags=alert_tags,
            raw_payload=payload
        )
        
        # Process the incident
        analysis = await process_incident(incident_request)
        
        # Send to Slack if configured
        if slack_service.is_configured():
            await slack_service.send_incident_analysis(analysis)
        
        return {
            "status": "success",
            "incident_id": analysis.incident_id,
            "analysis": analysis.dict()
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing incident: {str(e)}")


@app.post("/api/analyze")
async def analyze_incident(incident: IncidentRequest):
    try:
        analysis = await process_incident(incident)

        # Send to Slack if configured
        if slack_service.is_configured():
            await slack_service.send_incident_analysis(analysis)

        return {
            "status": "success",
            "analysis": analysis.dict()
        }
    except Exception as e:
        logger.error(f"Error analyzing incident: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing incident: {str(e)}")


async def process_incident(incident_request: IncidentRequest) -> IncidentAnalysis:
    """
    Main incident processing pipeline
    """
    logger.info(f"Processing incident: {incident_request.alert_title}")
    
    # Step 1: Collect context from Datadog
    logger.info("Fetching context from Datadog...")
    context = await datadog_service.fetch_incident_context(
        service_name=incident_request.service_name,
        alert_title=incident_request.alert_title,
        time_window_minutes=15
    )
    
    # Step 2: Analyze with Gemini
    logger.info("Analyzing with Gemini AI...")
    analysis = await gemini_service.analyze_incident(
        alert_title=incident_request.alert_title,
        alert_message=incident_request.alert_message,
        service_name=incident_request.service_name,
        context=context
    )
    
    # Step 3: Add metadata
    analysis.incident_id = f"inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    analysis.timestamp = datetime.now().isoformat()
    analysis.service_name = incident_request.service_name

    save_incident(analysis)
    
    logger.info(f"Incident analysis complete: {analysis.incident_id}")
    return analysis


@app.get("/api/incidents")
async def get_incidents_api():
    """
    Get recent incidents (in-memory for MVP)
    In production, this would query a database
    """
    items = get_incidents()
    return {
        "status": "success",
        "incidents": items,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

