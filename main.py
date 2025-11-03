from fastapi import FastAPI, Request
import json
import os
import httpx

# Load environment variables from Render (must set these in Render Dashboard)
INSTANTLY_API_KEY = os.getenv("YTg3NTg4ZDUtYzFlYi00YmVjLWJiMTEtNTAxMjdjODhmZGI2OnhKeHZ4dU1NdnVuRA==")
GHL_WEBHOOK_URL = os.getenv("https://services.leadconnectorhq.com/hooks/YY6x7gRvUfJYLcYjYg31/webhook-trigger/c6ba77bf-91f5-48ba-b331-fc0d38465662")

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Server running successfully on Render"}

@app.post("/webhook")
async def inbound_webhook(request: Request):
    try:
        data = await request.json()
        print("Received data from GHL:", json.dumps(data, indent=2))

        # Example: send this data to Instantly
        instantly_url = "https://api.instantly.ai/contacts/enrich"  # adjust path as needed
        headers = {"x-api-key": INSTANTLY_API_KEY, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            instantly_response = await client.post(instantly_url, json=data, headers=headers)
            instantly_json = instantly_response.json()
            print("Response from Instantly:", json.dumps(instantly_json, indent=2))

        # Send processed data to GHL
        payload_to_ghl = {
            "original_data": data,
            "instantly_result": instantly_json
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            ghl_response = await client.post(GHL_WEBHOOK_URL, json=payload_to_ghl)
            print("Response from GHL webhook:", ghl_response.text)

        return {"status": "success", "received": data}

    except httpx.HTTPError as e:
        print("HTTP error occurred:", str(e))
        return {"status": "fail", "reason": "HTTP error", "details": str(e)}
    except Exception as e:
        print("Unexpected error:", str(e))
        return {"status": "fail", "reason": "Unexpected error", "details": str(e)}

