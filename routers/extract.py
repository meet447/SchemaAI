from fastapi import Request, Depends, APIRouter
from fastapi.responses import JSONResponse
from services.extract.extract import extract
from services.extract.llm_normalization import llm_normalize

from core.auth import verify_api_key
import json

router = APIRouter()

@router.post("/extract")
async def generate_response(request: Request, api_key: str = Depends(verify_api_key)):
    payload = await request.json()
    url = payload.get('url')
    schema = payload.get('schema')
    advanced = payload.get('advanced', False)
    
    if not url or not schema:
        return JSONResponse(content={'error': 'Missing query or schema parameter'}, status_code=400)
    
    try:
        data = await extract(url, advanced)
        normalized_response = await llm_normalize(schema=schema, data=data)
        
        final_data = json.dumps(normalized_response)
        
        return JSONResponse(content=json.loads(final_data), status_code=200)
    except Exception as e:
        return JSONResponse(content={'error': str(e)}, status_code=500)