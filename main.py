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

# ===== EXISTING WEBHOOK LOGIC =====
@app.post("/webhook")
async def inbound_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raw_text = await request.body()
        payload = {"_raw_body": raw_text.decode(errors="ignore")}

    print("=== Incoming Webhook Payload ===")
    print(json.dumps(payload, indent=2))

    INSTANTLY_API_KEY = os.getenv("INSTANTLY_API_KEY")
    INSTANTLY_CAMPAIGN_ID = os.getenv("INSTANTLY_CAMPAIGN_ID")
    GHL_WEBHOOK_URL = os.getenv("GHL_WEBHOOK_URL")

    debug_env = {
        "INSTANTLY_API_KEY": masked(INSTANTLY_API_KEY),
        "INSTANTLY_CAMPAIGN_ID": masked(INSTANTLY_CAMPAIGN_ID),
        "GHL_WEBHOOK_URL": masked(GHL_WEBHOOK_URL)
    }
    print("Env check:", json.dumps(debug_env))

    if not INSTANTLY_API_KEY or not INSTANTLY_CAMPAIGN_ID:
        return {"status": "error", "detail": "Missing Instantly API key or Campaign ID"}

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

    instantly_url = "https://api.instantly.ai/api/v2/leads/import"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(instantly_url, headers=instantly_headers, json=lead_data)
            print("Instantly response:", resp.status_code, resp.text[:1000])
    except Exception as e:
        print("Instantly Exception:", type(e).__name__, str(e))
        print("Traceback:", traceback.format_exc())
        return {"status": "error", "stage": "instantly_push_failed", "error": str(e)}

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


# ===== NEW: Apollo Test Endpoint =====
@app.post("/test-pull-apollo")
async def test_pull_apollo():
    APOLLO_KEY = os.getenv("APOLLO_API_KEY")
    APOLLO_LIST = os.getenv("APOLLO_LIST_ID")
    INSTANTLY_KEY = os.getenv("INSTANTLY_API_KEY")
    INSTANTLY_CAMPAIGN = os.getenv("INSTANTLY_CAMPAIGN_ID")

    if not APOLLO_KEY or not APOLLO_LIST:
        return {"error": "Missing APOLLO_API_KEY or APOLLO_LIST_ID in env"}

    apollo_url = f"https://api.apollo.io/v1/lists/{APOLLO_LIST_ID}/people"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            headers = {"Authorization": f"Bearer {APOLLO_KEY}"}
            ap_res = await client.get(apollo_url, headers=headers)
            if ap_res.status_code != 200:
                return {"error": "apollo_error", "status": ap_res.status_code, "body": ap_res.text}
            ap_json = ap_res.json()
            people = ap_json.get("people") or ap_json.get("results") or ap_json.get("data") or ap_json
    except Exception as e:
        return {"error": "apollo_request_failed", "exception": str(e)}

    sample = []
    for p in (people if isinstance(people, list) else people.get("items", []))[:20]:
        sample.append({
            "email": p.get("email") or p.get("contact_email"),
            "first_name": p.get("first_name") or p.get("given_name") or "",
            "last_name": p.get("last_name") or p.get("family_name") or "",
            "company": p.get("company") or p.get("current_company") or "",
            "title": p.get("title") or p.get("job_title") or ""
        })

    sample = [s for s in sample if s.get("email")]

    if not sample:
        return {"error": "no_leads_from_apollo", "raw_people_count": len(people) if people else 0}

    if not INSTANTLY_KEY or not INSTANTLY_CAMPAIGN:
        return {"warning": "no_instantly_env_vars", "preview_count": len(sample), "sample": sample[:3]}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            inst_headers = {"x-api-key": INSTANTLY_KEY, "Content-Type": "application/json"}
            body = {"campaign_id": INSTANTLY_CAMPAIGN, "leads": sample}
            inst_res = await client.post("https://api.instantly.ai/api/v2/leads/import", headers=inst_headers, json=body)
            return {
                "apollo_count": len(sample),
                "instantly_status": inst_res.status_code,
                "instantly_body": inst_res.text[:1000]
            }
    except Exception as e:
        return {"error": "instantly_error", "exception": str(e)}
