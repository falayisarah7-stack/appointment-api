from fastapi import FastAPI
import os

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
@app.get("/test-ghl")
def test_ghl():
    api_key = os.getenv("GHL_API_KEY")
    base_url = os.getenv("GHL_BASE_URL")
    return {"GHL_API_KEY": api_key, "GHL_BASE_URL": base_url}

import requests

@app.get("/test-ghl-api")
def test_ghl_api():
    api_key = os.getenv("GHL_API_KEY")
    base_url = os.getenv("GHL_BASE_URL")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Example call: get locations linked to this account
    url = f"{base_url}/locations/"

    response = requests.get(url, headers=headers)
    try:
        data = response.json()
    except:
        data = {"error": "Failed to parse JSON"}

    return {
        "status_code": response.status_code,
        "data": data
    }
