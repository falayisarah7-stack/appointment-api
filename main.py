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
