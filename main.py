from fastapi import FastAPI, Request
import json
import os
import httpx
import traceback

app = FastAPI()

def masked(val):
    if not val:
        return None
    s = str(val)
    return s[:4] + "..." + s[-4:] if len(s) > 8 else s

@app.post("/webhook")
async def inbound_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raw_text = await request.body()
        payload = {"_raw_body": raw_text.decode(errors="ignore")}

    print("=== Incoming Webhook Payload ===")
    print(json.dumps(payload, indent=2))

    # ✅ Environment variables
    INSTANTLY_API_KEY = os.getenv("INSTANTLY_API_KEY")
    INSTANTLY_CAMPAIGN_ID = os.getenv("INSTANTLY_CAMPAIGN_ID")
    GHL_WEBHOOK_URL = os.getenv("GHL_WEBHOOK_URL")

    debug_env = {
        "INSTANTLY_API_KEY": masked(INSTANTLY_API_KEY),
        "INSTANTLY_CAMPAIGN_ID": masked(INSTANTLY_CAMPAIGN_ID),
        "GHL_WEBHOOK_URL": masked(GHL_WEBHOOK_URL)
    }
    print("Env check:", json.dumps(debug_env))

    # ✅ Basic validation
    if not INSTANTLY_API_KEY or not INSTANTLY_CAMPAIGN_ID:
        return {"status": "error", "detail": "Missing Instantly API key or Campaign ID"}

    # ✅ Prepare data for Instantly lead creation
    lead_data = {
        "campaignId": INSTANTLY_CAMPAIGN_ID,
        "leads": [
            {
                "email": payload.get("email") or payload.get("Email") or "unknown@example.com",
                "firstName": payload.get("first_name") or payload.get("First Name") or "",
                "lastName": payload.get("last_name") or payload.get("Last Name") or "",
                "companyName": payload.get("Deal Name / Company") or "",
                "customVariables": {
                    "industry": payload.get("Industry / Sector", ""),
                    "country": payload.get("Country", ""),
                    "ghl_id": payload.get("id", "")
                }
            }
        ]
    }

    print("=== Sending Lead to Instantly ===")
    print(json.dumps(lead_data, indent=2))

    instantly_headers = {
        "x-api-key": INSTANTLY_API_KEY,
        "Content-Type": "application/json"
    }

    instantly_url = "https://api.instantly.ai/api/v1/leads/add"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(instantly_url, headers=instantly_headers, json=lead_data)
            print("Instantly response:", resp.status_code, resp.text[:1000])
    except Exception as e:
        print("Instantly Exception:", type(e).__name__, str(e))
        print("Traceback:", traceback.format_exc())
        return {"status": "error", "stage": "instantly_push_failed", "error": str(e)}

    # ✅ Send confirmation to GHL inbound webhook
    if GHL_WEBHOOK_URL:
        try:
            ghl_payload = {
                "status": "Lead sent to Instantly",
                "instantly_status": resp.status_code,
                "deal_name": payload.get("Deal Name / Company", ""),
                "industry": payload.get("Industry / Sector", ""),
                "country": payload.get("Country", "")
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                ghl_resp = await client.post(GHL_WEBHOOK_URL, json=ghl_payload)
                print("GHL Webhook Response:", ghl_resp.status_code, ghl_resp.text[:500])
        except Exception as e:
            print("Error posting back to GHL:", str(e))

    return {"status": "success", "instantly_status": resp.status_code}
