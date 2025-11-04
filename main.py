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
    data = await request.json()
    print("Received:", json.dumps(data, indent=2))

    try:
        # Instantly API call
        async with httpx.AsyncClient() as client:
            instantly_response = await client.post(
                "https://api.instantly.ai/api/v1/contacts",
                headers={"x-api-key": INSTANTLY_API_KEY},
                json=data
            )
            instantly_data = instantly_response.json()

         # Send data back to GHL
        async with httpx.AsyncClient() as client:
            ghl_response = await client.post(GHL_WEBHOOK_URL, json=instantly_data)
            print("Sent back to GHL:", ghl_response.status_code)

        return {"status": "ok"}

    except Exception as e:
        print("Error:", e)
        return {"status": "failed", "error": str(e)}

@app.get("/")
def home():
    return {"message": "Server running successfully on Render"}
