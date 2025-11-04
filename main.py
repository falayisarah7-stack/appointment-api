from fastapi import FastAPI, Request
import json
import os
import httpx

app = FastAPI()

# Environment variables (set these in Render Dashboard > Environment)
INSTANTLY_API_KEY = os.getenv("INSTANTLY_API_KEY")
GHL_WEBHOOK_URL = os.getenv("GHL_WEBHOOK_URL")

@app.get("/")
def home():
    return {"message": "Server running successfully on Render"}

@app.post("/webhook")
async def inbound_webhook(request: Request):
    try:
        data = await request.json()
        print("Received data from GHL:", json.dumps(data, indent=2))

        # Step 1 — send data to Instantly API (example endpoint)
        instantly_url = "https://api.instantly.ai/api/v1/contacts/enrich"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": INSTANTLY_API_KEY
        }

        async with httpx.AsyncClient() as client:
            instantly_response = await client.post(instantly_url, headers=headers, json=data)
            instantly_result = instantly_response.json()
            print("Response from Instantly:", json.dumps(instantly_result, indent=2))

        # Step 2 — prepare payload for GHL
        payload_to_ghl = {
            "original_data": data,
            "instantly_result": instantly_result
        }

        async with httpx.AsyncClient() as client:
            ghl_response = await client.post(GHL_WEBHOOK_URL, json=payload_to_ghl)
            print("Data sent to GHL, status:", ghl_response.status_code)

        return {
            "status": "success",
            "instantly_status": instantly_response.status_code,
            "ghl_status": ghl_response.status_code
        }

    except Exception as e:
        print("Error processing webhook:", str(e))
        return {"status": "error", "detail": str(e)}

