import asyncio
import base64
import json
import aiohttp
import time
from solders.transaction import VersionedTransaction
from solders.message import Message
from solders.hash import Hash
from solders.pubkey import Pubkey
from solders.transaction import Transaction
import base58
from app.jupiter.token_list import MINT_DICT
from app.utils import crossmint
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from pprint import pprint
# Load environment variables
load_dotenv()

RPC_ENDPOINT = os.getenv("RPC_ENDPOINT")

timeout = aiohttp.ClientTimeout(total=10)


async def jupiter_swap(input_mint, output_mint, amount):
    
    WALLET_ADDRESS = await crossmint.fetch_wallet()

    quote_url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_mint}&outputMint={output_mint}&amount={amount}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(quote_url, timeout=timeout) as response:
                response.raise_for_status()
                quote_response = await response.json()
    except aiohttp.ClientError as e:
        print(f"Error getting quote from Jupiter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    swap_url = "https://quote-api.jup.ag/v6/swap"
    swap_data = {
        "quoteResponse": quote_response,
        "userPublicKey": str(WALLET_ADDRESS),
        "wrapUnwrapSOL": True
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(swap_url, json=swap_data, timeout=timeout) as response:
                response.raise_for_status()
                swap_response = await response.json()
    except aiohttp.ClientError as e:
        print(f"Error getting swap data from Jupiter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    try:
        instructions = []
        swap_transaction = swap_response['swapTransaction']
        transaction_bytes = base64.b64decode(swap_transaction)
        unsigned_tx = VersionedTransaction.from_bytes(transaction_bytes)
        message = unsigned_tx.message
        
        message_str = message.to_json()
        new_message = Message.from_json(message_str)
        ix = message.instructions
        
        # ix = message.instructions
        
        # # message.recent_blockhash = Hash.from_string("11111111111111111111111111111111")
        # # message.payer = Pubkey.from_string("11111111111111111111111111111112")
        # print(ix)
        # print(ix[0].json())

        new_message = Message.new_with_blockhash(
            instructions,
            Pubkey.from_string("11111111111111111111111111111112"),
            Hash.from_string("11111111111111111111111111111111")
        )
        transaction = Transaction.new_unsigned(new_message)
        serialized_transaction = bytes(transaction)
        serialized_transaction_str = base58.b58encode(serialized_transaction).decode('ascii')

        result = await crossmint.create_transaction(WALLET_ADDRESS,serialized_transaction_str)
        
        if not result:
            raise HTTPException(status_code=500, detail="Transaction sending failed")
        
        return result
        
    except Exception as e:
        print(f"Error creating or sending transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=e)

async def wait_for_confirmation(client, signature, max_timeout=60):
    start_time = time.time()
    while time.time() - start_time < max_timeout:
        try:
            status = await client.get_signature_statuses([signature])
            if status.value[0] is not None:
                return status.value[0].confirmation_status
        except Exception as e:
            print(f"Error checking transaction status: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
        await asyncio.sleep(1)
    return None

async def perform_swap(input_token, output_token, amount):
    print("swap")
    input_token_data = MINT_DICT.get(input_token)
    output_token_data = MINT_DICT.get(output_token)
    
    if not input_token_data:
        raise HTTPException(status_code=400, detail="The input token not found")
    if not output_token_data:
        raise HTTPException(status_code=400, detail="The output token not found")
    
    INPUT_MINT = input_token_data["MINT"]
    OUTPUT_MINT = output_token_data["MINT"]
    AMOUNT = amount * 10**input_token_data["DECIMALS"]

    try:
        result = await jupiter_swap(INPUT_MINT, OUTPUT_MINT, AMOUNT)
        if result:
            print(result)
            tx_sig = result["onChain"]["transaction"]
            solscan_url = f"https://solscan.io/tx/{tx_sig}"
            print(f"Solscan link: {solscan_url}")

            # Optional
            # async with AsyncClient(RPC_ENDPOINT) as client:
            #     confirmation_status = await wait_for_confirmation(client, tx_signature)
            #     print(f"Transaction confirmation status: {confirmation_status}")
            
            return {"status": "Transaction Success", "transaction_url": solscan_url}
        else:
            return {"status": "unable to swap"}
    except Exception as e:
        print(f"Error during swap: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
