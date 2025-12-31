"""
Test script for simulating Datadog webhooks
Usage: python test_webhook.py
"""

import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

def test_webhook():
    """Test the Datadog webhook endpoint"""
    
    # Sample Datadog webhook payload
    payload = {
        "title": "High Error Rate Detected",
        "text": "Error rate for api-service exceeded 5% threshold. Current error rate: 15.5%",
        "alert_status": "triggered",
        "tags": [
            "service:api-service",
            "env:production",
            "team:backend",
            "severity:high"
        ],
        "alert_type": "error_tracking",
        "date": datetime.now().isoformat(),
        "org": {
            "id": "12345",
            "name": "Demo Org"
        },
        "id": "test-alert-123"
    }
    
    print("🚀 Sending test webhook to Datadog endpoint...")
    print(f"📡 URL: {API_URL}/webhook/datadog")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/webhook/datadog",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        print("✅ Success!")
        print(f"📊 Response: {json.dumps(result, indent=2)}")
        
        if "analysis" in result:
            analysis = result["analysis"]
            print("\n" + "="*50)
            print("📋 INCIDENT ANALYSIS")
            print("="*50)
            print(f"Incident ID: {analysis.get('incident_id')}")
            print(f"Service: {analysis.get('service_name')}")
            print(f"Severity: {analysis.get('severity', 'N/A')}")
            print(f"Confidence: {analysis.get('confidence', 'N/A')}")
            print(f"\nSummary: {analysis.get('summary')}")
            print(f"\nRoot Cause: {analysis.get('root_cause')}")
            print(f"\nRecent Changes: {analysis.get('recent_changes')}")
            print(f"\nRecommended Actions:")
            for i, action in enumerate(analysis.get('recommended_actions', []), 1):
                print(f"  {i}. {action}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend.")
        print(f"   Make sure the backend is running at {API_URL}")
        print("   Start it with: cd backend && python -m uvicorn main:app --reload")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_analyze_endpoint():
    """Test the manual analyze endpoint"""
    
    payload = {
        "alert_title": "Database Connection Pool Exhausted",
        "alert_message": "Connection pool size exceeded maximum capacity",
        "service_name": "payment-service",
        "alert_tags": ["service:payment-service", "env:production"]
    }
    
    print("\n" + "="*50)
    print("🧪 Testing Manual Analyze Endpoint")
    print("="*50)
    print(f"📡 URL: {API_URL}/api/analyze")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/api/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        print("✅ Success!")
        print(f"📊 Response: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("="*50)
    print("🧪 AI Incident Responder - Test Script")
    print("="*50)
    print()
    
    # Test webhook endpoint
    test_webhook()
    
    # Test analyze endpoint
    test_analyze_endpoint()
    
    print("\n" + "="*50)
    print("✨ Testing complete!")
    print("="*50)


