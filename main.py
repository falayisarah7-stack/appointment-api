from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/webhook")
async def inbound_webhook(request: Request):
    data = await request.json()
    print("Received data:", json.dumps(data, indent=2))
    return {"status": "success", "received": data}

@app.get("/")
def home():
    return {"message": "Server running successfully on Render"}
