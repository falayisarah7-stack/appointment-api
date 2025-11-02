from fastapi import FastAPI
import os
import requests 

app = FastAPI()

# Example: Reading environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/")
def read_root():
    return {
        "message": "FastAPI app is running successfully!",
        "database_url": DATABASE_URL if DATABASE_URL else "No database URL found"
    }

# New endpoint to test GHL environment variables
@app.get("/test-ghl-api")
def test_ghl_api():
    import traceback
    api_key = os.getenv("GHL_API_KEY")
    base_url = os.getenv("GHL_BASE_URL")

    if not api_key:
        return {"error": "GHL_API_KEY not found in env"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # safe test path
    url = f"{base_url}/users/me"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        # return a safe error trace (no secrets)
        return {
            "status": "request_exception",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "trace": traceback.format_exc().splitlines()[-6:]
        }

    # return both status and body (if body is JSON, parse; otherwise return text)
    result = {"status_code": resp.status_code}
    try:
        result["body_json"] = resp.json()
    except Exception:
        # return beginning of text to avoid huge or secret dumps
        text = resp.text if len(resp.text) < 2000 else resp.text[:2000] + "...(truncated)"
        result["body_text_snippet"] = text

    return result
