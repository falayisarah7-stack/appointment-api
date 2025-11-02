from fastapi import FastAPI
import os, requests

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/send-contact-test")
def send_contact_test():
    import requests, json, os
    url = "https://services.leadconnectorhq.com/hooks/YY6x7gRvUfJYLcYjYg31/webhook-trigger/c6ba77bf-91f5-48ba-b331-fc0d38465662"
    payload = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890"
    }
    resp = requests.post(url, json=payload)
    return {"status_code": resp.status_code, "body": resp.text}
