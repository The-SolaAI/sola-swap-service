import requests
import os
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("CROSSMINT_API")

async def create_transaction(wallet,transaction):
    
    url = f"https://www.crossmint.com/api/v1-alpha2/wallets/{wallet}/transactions"
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "params": {
            "transaction": transaction
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

async def fetch_wallet():
    url = "https://www.crossmint.com/api/v1-alpha2/wallets"
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "solana-mpc-wallet",
        "linkedUser":"email:dummy@gmail.com"
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()['address']
