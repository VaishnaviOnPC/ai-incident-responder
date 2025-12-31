import requests
import time
import random

API = "https://ai-incident-responder-backend.onrender.com/api/analyze"

payloads = [
    {"alert_title": "High Error Rate", "alert_message": "5xx spike", "service_name": "api-service", "alert_tags": []},
    {"alert_title": "Latency Spike", "alert_message": "P95 > 2s", "service_name": "api-service", "alert_tags": []},
]

while True:
    data = random.choice(payloads)
    try:
        requests.post(API, json=data, timeout=5)
        print("Sent:", data["alert_title"])
    except Exception as e:
        print("Error:", e)
    time.sleep(5)
