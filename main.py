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
    if len(s) > 8:
        return s[:4] + "..." + s[-4:]
    return s

@app.post("/webhook")
async def inbound_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        text = await request.body()
        payload = {"_raw_body": text.decode(errors="ignore")}

    print("Received payload:", json.dumps(payload, indent=2))

    # ✅ Correct environment variable references
    INSTANTLY_API_KEY = os.getenv("INSTANTLY_API_KEY")
    GHL_WEBHOOK_URL = os.getenv("GHL_WEBHOOK_URL")
    GHL_API_KEY = os.getenv("GHL_API_KEY")
    GHL_BASE_URL = os.getenv("GHL_BASE_URL")

    debug_summary = {
        "INSTANTLY_API_KEY": masked(INSTANTLY_API_KEY),
        "GHL_WEBHOOK_URL": masked(GHL_WEBHOOK_URL),
        "GHL_API_KEY": masked(GHL_API_KEY),
        "GHL_BASE_URL": masked(GHL_BASE_URL)
    }
    print("Env debug:", json.dumps(debug_summary))

    missing = []
    if not INSTANTLY_API_KEY:
        missing.append("INSTANTLY_API_KEY")
    if missing:
        msg = {"error": "Missing required env variables", "missing": missing}
        print("ERROR:", msg)
        return {"status": "error", "detail": msg}

    headers = {"x-api-key": INSTANTLY_API_KEY}

    if any(v is None or not isinstance(v, (str, bytes)) for v in headers.values()):
        print("ERROR: header(s) not string-safe")
        return {"status": "error", "detail": "header value(s) must be str or bytes"}

    instantly_url = "https://api.instantly.ai/whatever-endpoint"  # Replace with real Instantly endpoint
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(instantly_url, json=payload, headers=headers)
            print("Instantly status:", resp.status_code, "body:", resp.text[:2000])
    except Exception as e:
        print("Instantly request exception:", type(e).__name__, str(e))
        print("Trace:", "\n".join(traceback.format_exc().splitlines()[-6:]))
        return {"status": "error", "stage": "instantly_call_failed", "error": str(e)}

    # ✅ Properly indented and simplified GHL webhook callback
    if GHL_WEBHOOK_URL:
        try:
            data_to_send = {
                "scoring_status": str(resp.status_code),
                "deal_name": payload.get("Deal Name / Company", ""),
                "industry": payload.get("Industry / Sector", ""),
                "country": payload.get("country", ""),
                "timestamp": payload.get("date_created", "")
            }

            print(f"Sending to GHL inbound webhook: {GHL_WEBHOOK_URL}")
            print(f"Payload being sent: {data_to_send}")

            async with httpx.AsyncClient(timeout=15.0) as client:
                ghl_resp = await client.post(GHL_WEBHOOK_URL, json=data_to_send)
                print("GHL webhook response:", ghl_resp.status_code, ghl_resp.text[:500])

        except Exception as e:
            print("Error sending data to GHL inbound webhook:", str(e))
    else:
        print("GHL_WEBHOOK_URL not found in environment.")

    return {"status": "success", "instantly_status": resp.status_code}

