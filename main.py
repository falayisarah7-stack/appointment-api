from fastapi import FastAPI
import os
import requests 

app = FastAPI()

# Example: Reading environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/")
def read_root():
    return {
        "message": "FastAPI app is running successfully!",
        "database_url": DATABASE_URL if DATABASE_URL else "No database URL found"
    }

# New endpoint to test GHL environment variables
@app.get("/send-webhook-test")
def send_webhook_test():
    import requests

    webhook_url = "https://services.leadconnectorhq.com/hooks/YY6x7gRvUfJYLcYjYg31/webhook-trigger/bc4c12a6-3c38-4038-845f-86e87847bd6d"

    data = {
        "client_name": "John Doe",
        "client_email": "john@example.com",
        "client_phone": "+1234567890",
        "deal_name": "Sample Investment Deal",
        "deal_amount": 50000,
        "deal_type": "Equity",
        "deal_stage": "Negotiation",
        "company_location": "New York"
    }

    response = requests.post(webhook_url, json=data)
    return {
        "status_code": response.status_code,
        "response_text": response.text
    }
