from fastapi import FastAPI, Request
import httpx
import json
import os

app = FastAPI()

# Your Instantly API Key (you can also use Render Environment Variables for safety)
INSTANTLY_API_KEY = "YTg3NTg4ZDUtYzFlYi00YmVjLWJiMTEtNTAxMjdjODhmZGI2OnhKeHZ4dU1NdnVuRA=="
# GHL webhook that receives processed data
GHL_WEBHOOK_URL = "https://services.leadconnectorhq.com/hooks/YY6x7gRvUfJYLcYjYg31/webhook-trigger/c6ba77bf-91f5-48ba-b331-fc0d38465662"


@app.post("/webhook")
async def inbound_webhook(request: Request):
    try:
        # Step 1: Receive data from GHL
        data = await request.json()
        print("✅ Received data from GHL:")
        print(json.dumps(data, indent=2))

        # Step 2: Send data to Instantly API
        async with httpx.AsyncClient() as client:
            instantly_response = await client.post(
                "https://api.instantly.ai/api/v1/contacts/enrich",  # Example endpoint
                headers={
                    "x-api-key": INSTANTLY_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "email": data.get("email") or data.get("contact", {}).get("email")
                }
            )

        instantly_data = instantly_response.json()
        print("⚙️ Instantly Response:")
        print(json.dumps(instantly_data, indent=2))

        # Step 3: Send processed/enriched data back to GHL webhook
        payload_to_ghl = {
            "original_data": data,
            "instantly_result": instantly_data
        }

        async with httpx.AsyncClient() as client:
            ghl_response = await client.post(GHL_WEBHOOK_URL, json=payload_to_ghl)
            print(f"📨 Sent enriched data to GHL: {ghl_response.status_code}")

        return {"status": "success", "instantly_data": instantly_data}

    except Exception as e:
        print("❌ Error processing webhook:", e)
        return {"status": "error", "message": str(e)}


@app.get("/")
def home():
    return {"message": "Server running successfully on Render"}
