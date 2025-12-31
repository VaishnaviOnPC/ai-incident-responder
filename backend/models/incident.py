"""
Data models for incident analysis
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class IncidentRequest(BaseModel):
    """Request model for incident analysis"""
    alert_title: str
    alert_message: str
    service_name: str
    alert_tags: List[str] = []
    raw_payload: Optional[Dict[str, Any]] = None


class IncidentContext(BaseModel):
    """Context data collected from Datadog"""
    logs: List[Dict[str, Any]] = []
    traces: List[Dict[str, Any]] = []
    metrics: Dict[str, Any] = {}
    recent_deployments: List[Dict[str, Any]] = []
    error_rate: Optional[float] = None
    latency_p95: Optional[float] = None


class IncidentAnalysis(BaseModel):
    """AI-generated incident analysis"""
    incident_id: Optional[str] = None
    timestamp: Optional[str] = None
    service_name: str
    summary: str
    root_cause: str
    recent_changes: str
    recommended_actions: List[str]
    confidence: str  # "low", "medium", "high"
    severity: Optional[str] = None  # "low", "medium", "high", "critical"
    raw_analysis: Optional[str] = None


