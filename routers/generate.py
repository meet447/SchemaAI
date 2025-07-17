from fastapi import Request, Depends, APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from services.generate.extract import extract
from services.generate.llm_normalization import llm_normalize, stream_normalization
from services.generate.search import generate_and_run_searches
from core.auth import verify_api_key
import json

router = APIRouter()

@router.post("/generate")
async def generate_response(request: Request, api_key: str = Depends(verify_api_key)):
    payload = await request.json()
    query = payload.get('query')
    schema = payload.get('schema')
    stream = payload.get('stream', False)

    if not query or not schema:
        return JSONResponse(content={'error': 'Missing query or schema parameter'}, status_code=400)

    # This is the main async generator for the entire process
    async def process_and_stream():
        # 1. Immediately yield a status update
        yield f"data: {json.dumps({'status': 'Generating search queries...'})}\n\n"
        search_results = await generate_and_run_searches(query)

        # 2. Yield another update before extraction
        yield f"data: {json.dumps({'status': 'Extracting content from sources...'})}\n\n"
        response_data = await extract(search_results)

        # 3. Yield a final status update before normalization
        yield f"data: {json.dumps({'status': 'Normalizing data with LLM...'})}\n\n"

        # 4. Stream the final normalized data from the LLM
        # This will yield the actual JSON objects as they are generated
        async for chunk in stream_normalization(query=query, data=response_data, schema=schema):
            yield chunk # The chunk already includes the "data: " prefix and "\n\n" suffix

    if stream:
        return StreamingResponse(
            process_and_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        # Non-streaming logic remains the same
        search_results = await generate_and_run_searches(query)
        response_data = await extract(search_results)
        final_data = await llm_normalize(query=query, data=response_data, schema=schema)
        return JSONResponse(content=json.loads(final_data), status_code=200)