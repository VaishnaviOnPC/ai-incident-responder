"""
Datadog API integration for fetching logs, traces, and metrics
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.incident import IncidentContext

logger = logging.getLogger(__name__)


class DatadogService:
    """Service for interacting with Datadog API"""
    
    def __init__(self):
        self.api_key = os.getenv("DATADOG_API_KEY")
        self.app_key = os.getenv("DATADOG_APP_KEY")
        self.site = os.getenv("DATADOG_SITE", "datadoghq.com")
        self.base_url = f"https://api.{self.site}"
        
        if not self.api_key or not self.app_key:
            logger.warning("Datadog credentials not configured. Using mock data.")
    
    def is_configured(self) -> bool:
        """Check if Datadog is properly configured"""
        return bool(self.api_key and self.app_key)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        return {
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key,
            "Content-Type": "application/json"
        }
    
    async def fetch_incident_context(
        self,
        service_name: str,
        alert_title: str,
        time_window_minutes: int = 15
    ) -> IncidentContext:
        """
        Fetch comprehensive context for an incident
        """
        if not self.is_configured():
            logger.info("Datadog not configured, returning mock context")
            return self._get_mock_context(service_name)
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=time_window_minutes)
            
            # Fetch logs, traces, and metrics in parallel
            logs = await self._fetch_logs(service_name, start_time, end_time)
            traces = await self._fetch_traces(service_name, start_time, end_time)
            metrics = await self._fetch_metrics(service_name, start_time, end_time)
            deployments = await self._fetch_recent_deployments(service_name)
            
            # Calculate error rate and latency
            error_rate = self._calculate_error_rate(logs, metrics)
            latency_p95 = self._calculate_latency_p95(traces, metrics)
            
            return IncidentContext(
                logs=logs[:50],  # Limit to 50 most recent logs
                traces=traces[:20],  # Limit to 20 most recent traces
                metrics=metrics,
                recent_deployments=deployments,
                error_rate=error_rate,
                latency_p95=latency_p95
            )
            
        except Exception as e:
            logger.error(f"Error fetching Datadog context: {str(e)}", exc_info=True)
            # Return mock data on error
            return self._get_mock_context(service_name)
    
    async def _fetch_logs(self, service_name: str, start_time: datetime, end_time: datetime):
        try:
            url = f"{self.base_url}/api/v2/logs/events/search"
            payload = {
                "filter": {
                    "query": f"service:{service_name}",
                    "from": start_time.isoformat(),
                    "to": end_time.isoformat()
                },
                "page": {"limit": 50},
                "sort": "-timestamp"
            }

            response = requests.post(url, headers=self._get_headers(), json=payload, timeout=10)
            response.raise_for_status()

            return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Error fetching logs: {e}")
            return []
    
    async def _fetch_traces(self, service_name: str, start_time: datetime, end_time: datetime):
        try:
            url = f"{self.base_url}/api/v2/traces/events/search"
            payload = {
                "filter": {
                    "query": f"service:{service_name}",
                    "from": start_time.isoformat(),
                    "to": end_time.isoformat()
                },
                "page": {"limit": 20},
                "sort": "-timestamp"
            }

            response = requests.post(url, headers=self._get_headers(), json=payload, timeout=10)
            response.raise_for_status()

            return response.json().get("data", [])
        except Exception as e:
            logger.warning(f"Traces unavailable: {e}")
            return []
    
    async def _fetch_metrics(self, service_name: str, start_time: datetime, end_time: datetime):
        try:
            url = f"{self.base_url}/api/v1/query"
            query = f"avg:http.request.duration{{service:{service_name}}}.rollup(p95)"

            params = {
                "query": query,
                "from": int(start_time.timestamp()),
                "to": int(end_time.timestamp())
            }

            response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return {}
    
    async def _fetch_recent_deployments(
        self,
        service_name: str
    ) -> List[Dict[str, Any]]:
        """Fetch recent deployments (mock for MVP)"""
        # In production, integrate with your deployment tracking system
        # This could be Datadog Events, GitHub Actions, or a deployment API
        return [
            {
                "version": "v1.4.2",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "service": service_name
            }
        ]
    
    def _calculate_error_rate(
        self,
        logs: List[Dict[str, Any]],
        metrics: Dict[str, Any]
    ) -> Optional[float]:
        """Calculate error rate from logs and metrics"""
        if not logs:
            return None
        
        error_count = len([log for log in logs if log.get("status") == "error"])
        total_count = len(logs)
        
        if total_count == 0:
            return None
        
        return (error_count / total_count) * 100
    
    def _calculate_latency_p95(
        self,
        traces: List[Dict[str, Any]],
        metrics: Dict[str, Any]
    ) -> Optional[float]:
        """Calculate P95 latency"""
        # Extract from metrics if available
        if metrics.get("latency"):
            series = metrics["latency"]
            if series and len(series) > 0:
                points = series[0].get("pointlist", [])
                if points:
                    return points[-1][1]  # Last value
        
        # Fallback: calculate from traces
        if traces:
            durations = [t.get("duration", 0) for t in traces if t.get("duration")]
            if durations:
                sorted_durations = sorted(durations)
                p95_index = int(len(sorted_durations) * 0.95)
                return sorted_durations[p95_index]
        
        return None
    
    def _get_mock_context(self, service_name: str) -> IncidentContext:
        """Generate mock context for testing/demo"""
        return IncidentContext(
            logs=[
                {
                    "message": f"[ERROR] Database connection pool exhausted in {service_name}",
                    "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                    "status": "error",
                    "service": service_name
                },
                {
                    "message": f"[ERROR] Timeout waiting for connection in {service_name}",
                    "timestamp": (datetime.now() - timedelta(minutes=4)).isoformat(),
                    "status": "error",
                    "service": service_name
                }
            ],
            traces=[
                {
                    "service": service_name,
                    "duration": 5000,
                    "status": "error",
                    "operation": "database.query"
                }
            ],
            metrics={
                "error_rate": 15.5,
                "latency_p95": 2500
            },
            recent_deployments=[
                {
                    "version": "v1.4.2",
                    "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                    "service": service_name
                }
            ],
            error_rate=15.5,
            latency_p95=2500.0
        )

