from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.jupiter.swap import perform_swap

class SwapRequest(BaseModel):
    input_token : str
    output_token : str
    amount : int

swap_router = APIRouter()

@swap_router.post("/swap")
async def swap_tokens(request : SwapRequest):
    print(request)
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    try:
        result = await perform_swap(request.input_token, request.output_token, request.amount)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=e)
