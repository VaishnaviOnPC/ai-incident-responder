import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { AlertTriangle, CheckCircle, Clock, Activity, Zap } from 'lucide-react'
import './App.css'

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

function App() {
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [testAlert, setTestAlert] = useState({
    alert_title: 'High Error Rate Detected',
    alert_message: 'Error rate exceeded 5% threshold',
    service_name: 'api-service',
    alert_tags: ['service:api-service', 'env:production']
  })

  useEffect(() => {
    // Poll for incidents (in production, use WebSockets or SSE)
    const interval = setInterval(() => {
      fetchIncidents()
    }, 10000) // Poll every 10 seconds

    fetchIncidents()
    return () => clearInterval(interval)
  }, [])

  const fetchIncidents = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/incidents`)
      if (response.data.incidents) {
        setIncidents(response.data.incidents)
      }
    } catch (error) {
      console.error('Error fetching incidents:', error)
    }
  }

  const handleTestAlert = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE_URL}/api/analyze`, testAlert)
      const analysis = response.data.analysis
      
      // Add to incidents list
      const newIncident = {
        ...analysis,
        id: analysis.incident_id,
        timestamp: analysis.timestamp || new Date().toISOString()
      }
      setIncidents([newIncident, ...incidents])
      setSelectedIncident(newIncident)
    } catch (error) {
      console.error('Error analyzing incident:', error)
      alert('Error analyzing incident. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return '#ef4444'
      case 'high':
        return '#f97316'
      case 'medium':
        return '#eab308'
      case 'low':
        return '#22c55e'
      default:
        return '#6b7280'
    }
  }

  const getConfidenceColor = (confidence) => {
    switch (confidence?.toLowerCase()) {
      case 'high':
        return '#22c55e'
      case 'medium':
        return '#eab308'
      case 'low':
        return '#f97316'
      default:
        return '#6b7280'
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="header-title">
            <Zap className="header-icon" />
            <h1>AI Incident Responder</h1>
          </div>
          <p className="header-subtitle">
            Real-time AI-powered incident analysis and remediation
          </p>
        </div>
      </header>

      <div className="container">
        <div className="main-content">
          {/* Test Alert Section */}
          <div className="card test-alert-card">
            <h2>Test Incident Analysis</h2>
            <div className="test-form">
              <div className="form-group">
                <label>Alert Title</label>
                <input
                  type="text"
                  value={testAlert.alert_title}
                  onChange={(e) => setTestAlert({ ...testAlert, alert_title: e.target.value })}
                  placeholder="High Error Rate Detected"
                />
              </div>
              <div className="form-group">
                <label>Service Name</label>
                <input
                  type="text"
                  value={testAlert.service_name}
                  onChange={(e) => setTestAlert({ ...testAlert, service_name: e.target.value })}
                  placeholder="api-service"
                />
              </div>
              <div className="form-group">
                <label>Alert Message</label>
                <textarea
                  value={testAlert.alert_message}
                  onChange={(e) => setTestAlert({ ...testAlert, alert_message: e.target.value })}
                  placeholder="Error rate exceeded threshold"
                  rows="3"
                />
              </div>
              <button
                className="btn-primary"
                onClick={handleTestAlert}
                disabled={loading}
              >
                {loading ? 'Analyzing...' : 'Analyze Incident'}
              </button>
            </div>
          </div>

          {/* Incident Analysis Display */}
          {selectedIncident && (
            <div className="card incident-analysis">
              <div className="incident-header">
                <div>
                  <h2>Incident Analysis</h2>
                  <p className="incident-id">ID: {selectedIncident.incident_id}</p>
                </div>
                <div className="incident-badges">
                  <span
                    className="badge"
                    style={{ backgroundColor: getSeverityColor(selectedIncident.severity) }}
                  >
                    {selectedIncident.severity?.toUpperCase() || 'UNKNOWN'}
                  </span>
                  <span
                    className="badge"
                    style={{ backgroundColor: getConfidenceColor(selectedIncident.confidence) }}
                  >
                    {selectedIncident.confidence?.toUpperCase() || 'MEDIUM'} Confidence
                  </span>
                </div>
              </div>

              <div className="analysis-section">
                <h3>
                  <AlertTriangle className="section-icon" />
                  Summary
                </h3>
                <p>{selectedIncident.summary}</p>
              </div>

              <div className="analysis-section">
                <h3>
                  <Activity className="section-icon" />
                  Root Cause
                </h3>
                <p>{selectedIncident.root_cause}</p>
              </div>

              <div className="analysis-section">
                <h3>
                  <Clock className="section-icon" />
                  Recent Changes
                </h3>
                <p>{selectedIncident.recent_changes}</p>
              </div>

              <div className="analysis-section">
                <h3>
                  <CheckCircle className="section-icon" />
                  Recommended Actions
                </h3>
                <ul className="actions-list">
                  {selectedIncident.recommended_actions?.map((action, index) => (
                    <li key={index}>{action}</li>
                  ))}
                </ul>
              </div>

              {selectedIncident.timestamp && (
                <div className="incident-footer">
                  <p>Analyzed at: {new Date(selectedIncident.timestamp).toLocaleString()}</p>
                </div>
              )}
            </div>
          )}

          {/* Placeholder when no incident selected */}
          {!selectedIncident && (
            <div className="card placeholder-card">
              <Zap className="placeholder-icon" />
              <h2>No Incident Selected</h2>
              <p>Use the test form above to analyze an incident, or wait for a Datadog webhook.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App


