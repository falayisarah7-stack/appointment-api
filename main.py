from fastapi import FastAPI
import os, requests

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/send-test-webhook")
def send_test_webhook():
    url = "https://services.leadconnectorhq.com/hooks/YY6x7gRvUfJYLcYjYg31/webhook-trigger/bc4c12a6-3c38-4038-845f-86e87847bd6d"

    payload = {
        "test_contact": {
            "firstName": "Sarah",
            "lastName": "Falayi",
            "email": "sarah@example.com",
            "phone": "+2340000000000"
        },
        "meta": {"source": "Render Webhook Test"}
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return {
            "status_code": response.status_code,
            "body": response.text
        }
    except Exception as e:
        return {"error": str(e)}
