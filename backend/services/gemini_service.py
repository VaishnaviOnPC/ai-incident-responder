"""
Google AI Studio Gemini integration for incident analysis
Uses the google-generativeai library for Google AI Studio API
"""

import os
import logging
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.incident import IncidentAnalysis, IncidentContext

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            logger.warning("Gemini API key not configured. Using mock responses.")
            self.model = None
    
    def is_configured(self) -> bool:
        """Check if Gemini is properly configured"""
        return bool(self.api_key and self.model)
    
    async def analyze_incident(
        self,
        alert_title: str,
        alert_message: str,
        service_name: str,
        context: IncidentContext
    ) -> IncidentAnalysis:
        """
        Analyze incident using Gemini AI
        """
        if not self.is_configured():
            logger.info("Gemini not configured, returning mock analysis")
            return self._get_mock_analysis(alert_title, service_name, context)
        
        try:
            # Build the prompt
            prompt = self._build_analysis_prompt(
                alert_title=alert_title,
                alert_message=alert_message,
                service_name=service_name,
                context=context
            )
            
            # Call Gemini
            logger.info("Calling Gemini API...")
            response = self.model.generate_content(prompt)
            
            # Parse the response
            analysis = self._parse_gemini_response(
                response_text=response.text,
                alert_title=alert_title,
                service_name=service_name
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing with Gemini: {str(e)}", exc_info=True)
            # Fallback to mock analysis
            return self._get_mock_analysis(alert_title, service_name, context)
    
    def _build_analysis_prompt(
        self,
        alert_title: str,
        alert_message: str,
        service_name: str,
        context: IncidentContext
    ) -> str:
        """
        Build the prompt for Gemini analysis
        This is the KEY part for quality analysis
        """
        # Format logs
        log_summary = ""
        if context.logs:
            log_summary = "\n".join([
                f"- {log.get('message', 'N/A')} [{log.get('timestamp', 'N/A')}]"
                for log in context.logs[:10]  # Top 10 logs
            ])
        else:
            log_summary = "No recent error logs found."
        
        # Format traces
        trace_summary = ""
        if context.traces:
            trace_summary = "\n".join([
                f"- {trace.get('operation', 'N/A')}: {trace.get('duration', 0)}ms [{trace.get('status', 'N/A')}]"
                for trace in context.traces[:10]
            ])
        else:
            trace_summary = "No recent traces found."
        
        # Format deployments
        deploy_summary = ""
        if context.recent_deployments:
            deploy_summary = "\n".join([
                f"- {deploy.get('version', 'N/A')} deployed at {deploy.get('timestamp', 'N/A')}"
                for deploy in context.recent_deployments
            ])
        else:
            deploy_summary = "No recent deployments found."
        
        prompt = f"""You are an expert Site Reliability Engineer (SRE) with deep experience in production incident analysis.

Given the following incident context, provide a structured analysis:

## Alert Information
- **Title**: {alert_title}
- **Message**: {alert_message}
- **Service**: {service_name}
- **Error Rate**: {context.error_rate}% (if available)
- **P95 Latency**: {context.latency_p95}ms (if available)

## Recent Error Logs
{log_summary}

## Recent Traces
{trace_summary}

## Recent Deployments
{deploy_summary}

## Metrics Summary
{json.dumps(context.metrics, indent=2) if context.metrics else "No metrics available"}

---

Please provide your analysis in the following JSON format:

{{
  "summary": "A brief 2-3 sentence summary of what is likely going wrong",
  "root_cause": "Your assessment of the most likely root cause based on the evidence",
  "recent_changes": "What changed recently that might have caused this (deployments, config changes, etc.)",
  "recommended_actions": [
    "Action 1: Specific, actionable step",
    "Action 2: Another specific step",
    "Action 3: Additional step if needed"
  ],
  "confidence": "low|medium|high",
  "severity": "low|medium|high|critical"
}}

Be specific, actionable, and base your analysis on the evidence provided. If you're uncertain, indicate low confidence."""
        
        return prompt
    
    def _parse_gemini_response(
        self,
        response_text: str,
        alert_title: str,
        service_name: str
    ) -> IncidentAnalysis:
        """
        Parse Gemini's response into IncidentAnalysis model
        """
        try:
            # Try to extract JSON from the response
            # Gemini might wrap JSON in markdown code blocks
            text = response_text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            text = text.strip()
            
            # Parse JSON
            data = json.loads(text)
            
            return IncidentAnalysis(
                service_name=service_name,
                summary=data.get("summary", "Analysis unavailable"),
                root_cause=data.get("root_cause", "Root cause unknown"),
                recent_changes=data.get("recent_changes", "No recent changes identified"),
                recommended_actions=data.get("recommended_actions", []),
                confidence=data.get("confidence", "medium"),
                severity=data.get("severity", "medium"),
                raw_analysis=response_text
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            
            # Fallback: try to extract information from text
            return self._parse_text_response(response_text, alert_title, service_name)
    
    def _parse_text_response(
        self,
        response_text: str,
        alert_title: str,
        service_name: str
    ) -> IncidentAnalysis:
        """
        Fallback parser for non-JSON responses
        """
        # Simple text parsing - extract key sections
        lines = response_text.split("\n")
        
        summary = ""
        root_cause = ""
        recent_changes = ""
        actions = []
        confidence = "medium"
        severity = "medium"
        
        current_section = None
        for line in lines:
            line_lower = line.lower().strip()
            if "summary" in line_lower:
                current_section = "summary"
            elif "root cause" in line_lower:
                current_section = "root_cause"
            elif "recent changes" in line_lower or "what changed" in line_lower:
                current_section = "recent_changes"
            elif "action" in line_lower or "recommend" in line_lower:
                current_section = "actions"
            elif "confidence" in line_lower:
                if "low" in line_lower:
                    confidence = "low"
                elif "high" in line_lower:
                    confidence = "high"
            elif "severity" in line_lower:
                if "critical" in line_lower:
                    severity = "critical"
                elif "high" in line_lower:
                    severity = "high"
                elif "low" in line_lower:
                    severity = "low"
            else:
                if current_section == "summary" and line.strip():
                    summary += line.strip() + " "
                elif current_section == "root_cause" and line.strip():
                    root_cause += line.strip() + " "
                elif current_section == "recent_changes" and line.strip():
                    recent_changes += line.strip() + " "
                elif current_section == "actions" and line.strip() and line.strip().startswith("-"):
                    actions.append(line.strip().lstrip("- ").strip())
        
        return IncidentAnalysis(
            service_name=service_name,
            summary=summary.strip() or "Analysis generated from text response",
            root_cause=root_cause.strip() or "Root cause analysis unavailable",
            recent_changes=recent_changes.strip() or "No recent changes identified",
            recommended_actions=actions if actions else ["Review logs and metrics for more details"],
            confidence=confidence,
            severity=severity,
            raw_analysis=response_text
        )
    
    def _get_mock_analysis(
        self,
        alert_title: str,
        service_name: str,
        context: IncidentContext
    ) -> IncidentAnalysis:
        """Generate mock analysis for testing/demo"""
        return IncidentAnalysis(
            service_name=service_name,
            summary=f"High error rate detected in {service_name}. Database connection pool appears to be exhausted, causing timeouts and failed requests.",
            root_cause="Database connection pool exhaustion likely caused by deployment v1.4.2 which introduced a connection leak. The pool size may be insufficient for current load.",
            recent_changes="Deployment v1.4.2 was deployed 30 minutes ago. This deployment included changes to database connection handling.",
            recommended_actions=[
                "1. Check database connection pool metrics and current pool usage",
                "2. Review deployment v1.4.2 changes related to database connections",
                "3. Consider temporarily increasing connection pool size",
                "4. Look for connection leaks in the recent code changes",
                "5. Monitor error rate after applying fixes"
            ],
            confidence="high",
            severity="high",
            raw_analysis="Mock analysis - Gemini API not configured"
        )

