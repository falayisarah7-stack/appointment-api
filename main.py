from fastapi import FastAPI, Request
import json
import os
import httpx
import traceback

app = FastAPI()

# Helper: safe masked print for keys (do not print secrets in public chat)
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

    # 1) Log inbound payload (already done but keep it)
    print("Received payload:", json.dumps(payload, indent=2))

    # 2) Read environment variables used for outgoing calls
    INSTANTLY_API_KEY = os.getenv("YTg3NTg4ZDUtYzFlYi00YmVjLWJiMTEtNTAxMjdjODhmZGI2OnhKeHZ4dU1NdnVuRA==")
    GHL_WEBHOOK_URL = os.getenv("https://services.leadconnectorhq.com/hooks/YY6x7gRvUfJYLcYjYg31/webhook-trigger/c6ba77bf-91f5-48ba-b331-fc0d38465662")
    GHL_API_KEY = os.getenv("pit-2bea1d2d-a72f-4814-8f13-d93d9b0cebc4")
    GHL_BASE_URL = os.getenv("https://services.leadconnectorhq.com")

    # 3) Quick debug summary (masked)
    debug_summary = {
        "INSTANTLY_API_KEY": masked(INSTANTLY_API_KEY),
        "GHL_WEBHOOK_URL": masked(GHL_WEBHOOK_URL),
        "GHL_API_KEY": masked(GHL_API_KEY),
        "GHL_BASE_URL": masked(GHL_BASE_URL)
    }
    print("Env debug:", json.dumps(debug_summary))

    # 4) Validate required values and fail with clear message if missing
    missing = []
    if not INSTANTLY_API_KEY:
        missing.append("INSTANTLY_API_KEY")
    # GHL_WEBHOOK_URL may be optional for some tests - include if your flow needs it
    if missing:
        msg = {"error": "Missing required env variables", "missing": missing}
        print("ERROR:", msg)
        return {"status": "error", "detail": msg}

    # 5) Prepare outgoing headers carefully and validate types
    headers = {
        "x-api-key": INSTANTLY_API_KEY,
        # add more headers only if values exist
    }

    # Defensive check: ensure all header values are str
    bad_headers = {k: type(v).__name__ for k, v in headers.items() if v is None or not isinstance(v, (str, bytes))}
    if bad_headers:
        print("ERROR: header(s) not string-safe:", bad_headers)
        return {"status": "error", "detail": "header value(s) must be str or bytes", "bad_headers": bad_headers}

    # 6) Example: call Instantly (adjust endpoint path later)
    instantly_url = "https://api.instantly.ai/whatever-endpoint"  # placeholder — replace with real endpoint
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(instantly_url, json=payload, headers=headers)
            resp_text = resp.text[:2000]
            print("Instantly status:", resp.status_code, "body:", resp_text)
    except Exception as e:
        print("Instantly request exception:", type(e).__name__, str(e))
        print("Trace:", "\n".join(traceback.format_exc().splitlines()[-6:]))
        return {"status": "error", "stage": "instantly_call_failed", "error": str(e)}

    # 7) Send result back to GHL webhook (if applicable)
if GHL_WEBHOOK_URL:
    try:
        # Prepare a simplified payload to avoid nesting issues in GHL
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
