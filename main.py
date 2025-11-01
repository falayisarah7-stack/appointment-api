from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

# Basic test route
@app.get("/test")
def read_root():
    return {"message": "FastAPI is running successfully on Render!"}

# Placeholder model for deal scoring
class DealData(BaseModel):
    deal_name: str
    deal_amount: float | None = None
    deal_type: str | None = None
    deal_stage: str | None = None
    client_name: str | None = None
    client_email: str | None = None
    client_phone: str | None = None
    company_industry: str | None = None
    company_location: str | None = None

@app.post("/score-deal")
async def score_deal(data: DealData):
    # Placeholder logic – later we’ll replace this with actual scoring
    return {
        "deal_name": data.deal_name,
        "status": "received",
        "message": "Webhook successfully connected and data captured."
    }
  
