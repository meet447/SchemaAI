from fastapi import Request
from fastapi.exceptions import HTTPException

def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != "test":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key