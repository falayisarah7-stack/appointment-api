from fastapi import FastAPI, Request
import json
import os
import httpx

app = FastAPI()

INSTANTLY_API_KEY = os.getenv("YTg3NTg4ZDUtYzFlYi00YmVjLWJiMTEtNTAxMjdjODhmZGI2OnhKeHZ4dU1NdnVuRA==")
GHL_WEBHOOK_URL = os.getenv("https://services.leadconnectorhq.com/hooks/YY6x7gRvUfJYLcYjYg31/webhook-trigger/c6ba77bf-91f5-48ba-b331-fc0d38465662")

@app.post("/webhook")
async def inbound_webhook(request: Request):
    data = await request.json()
    print("Received data:", json.dumps(data, indent=2))

    # send data to GHL
    payload_to_ghl = {"contact": data}  # adjust as needed
    try:
        async with httpx.AsyncClient() as client:
            ghl_response = await client.post(GHL_WEBHOOK_URL, json=payload_to_ghl)
        print("GHL response:", ghl_response.status_code, ghl_response.text)
    except Exception as e:
        print("Error sending to GHL:", str(e))

    return {"status": "success", "received": data}

@app.get("/")
def home():
    return {"message": "Server running successfully on Render"}
