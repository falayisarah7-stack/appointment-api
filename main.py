from fastapi import FastAPI, Request
import json
import os
import httpx

app = FastAPI()

# Environment variables (set these in Render Dashboard > Environment)
INSTANTLY_API_KEY = os.getenv("YTg3NTg4ZDUtYzFlYi00YmVjLWJiMTEtNTAxMjdjODhmZGI2OnhKeHZ4dU1NdnVuRA==")
GHL_WEBHOOK_URL = os.getenv("https://services.leadconnectorhq.com/hooks/YY6x7gRvUfJYLcYjYg31/webhook-trigger/c6ba77bf-91f5-48ba-b331-fc0d38465662")

@app.post("/webhook")
async def inbound_webhook(request: Request):
    try:
        # Step 1: Receive data from GHL
        incoming_data = await request.json()
        print("✅ Incoming data from GHL:")
        print(json.dumps(incoming_data, indent=2))

        # Step 2: Send data to Instantly API
        instantly_payload = {
            "firstName": incoming_data.get("firstName"),
            "lastName": incoming_data.get("lastName"),
            "email": incoming_data.get("email"),
            "phone": incoming_data.get("phone")
        }

        instantly_headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": INSTANTLY_API_KEY
        }

        async with httpx.AsyncClient() as client:
            instantly_response = await client.post(
                "https://api.instantly.ai/api/v1/contacts",  # example endpoint
                headers=instantly_headers,
                json=instantly_payload
            )

        print("✅ Instantly response:")
        print(instantly_response.text)

        # Step 3: Send processed data back to GHL
        payload_to_ghl = {
            "contact_name": f"{incoming_data.get('firstName', '')} {incoming_data.get('lastName', '')}",
            "email": incoming_data.get("email"),
            "phone": incoming_data.get("phone"),
            "source": "Instantly API",
            "score": "85",  # Example static score (replace with real data later)
            "status": "Processed by Render"
        }

        async with httpx.AsyncClient() as client:
            ghl_response = await client.post(GHL_WEBHOOK_URL, json=payload_to_ghl)

        print("✅ GHL response:", ghl_response.text)

        return {"status": "success", "message": "Data processed and sent back to GHL"}

    except Exception as e:
        print("❌ Error:", str(e))
        return {"status": "error", "message": str(e)}

@app.get("/")
def home():
    return {"message": "Server running successfully on Render"}
