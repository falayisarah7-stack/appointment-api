from fastapi import FastAPI
import os, requests

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/send-test-webhook")
def send_test_webhook():
    url = "https://services.leadconnectorhq.com/hooks/YY6x7gRvUfJYLcYjYg31/webhook-trigger/c6ba77bf-91f5-48ba-b331-fc0d38465662"

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
