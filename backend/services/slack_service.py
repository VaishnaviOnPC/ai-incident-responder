"""
Slack integration for sending incident notifications
"""

import os
import logging
import requests
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.incident import IncidentAnalysis

logger = logging.getLogger(__name__)


class SlackService:
    """Service for sending notifications to Slack"""
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    def is_configured(self) -> bool:
        """Check if Slack is properly configured"""
        return bool(self.webhook_url)
    
    async def send_incident_analysis(self, analysis: IncidentAnalysis) -> bool:
        """
        Send incident analysis to Slack
        """
        if not self.is_configured():
            logger.info("Slack not configured, skipping notification")
            return False
        
        try:
            # Build Slack message
            message = self._build_slack_message(analysis)
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Sent incident analysis to Slack: {analysis.incident_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending to Slack: {str(e)}", exc_info=True)
            return False
    
    def _build_slack_message(self, analysis: IncidentAnalysis) -> dict:
        """
        Build Slack message payload
        """
        # Determine color based on severity
        color_map = {
            "critical": "#FF0000",  # Red
            "high": "#FF9900",      # Orange
            "medium": "#FFCC00",    # Yellow
            "low": "#36A64F"        # Green
        }
        color = color_map.get(analysis.severity or "medium", "#FFCC00")
        
        # Format actions
        actions_text = "\n".join([
            f"• {action}" for action in analysis.recommended_actions
        ])
        
        message = {
            "text": f"🚨 Incident Detected: {analysis.service_name}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 Incident: {analysis.service_name}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Incident ID:*\n`{analysis.incident_id}`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:*\n{analysis.severity.upper() if analysis.severity else 'UNKNOWN'}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Confidence:*\n{analysis.confidence.upper()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Time:*\n{analysis.timestamp or 'N/A'}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{analysis.summary}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Root Cause:*\n{analysis.root_cause}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Recent Changes:*\n{analysis.recent_changes}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Recommended Actions:*\n{actions_text}"
                    }
                }
            ]
        }
        
        return message

