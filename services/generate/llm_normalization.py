import json
from core.llm import generate_response, generate_response_google, stream_response, stream_response_google
from config import SERVICE, MODEL

def format_sources_for_prompt(sources):
    formatted = ""
    for i, item in enumerate(sources, 1):
        url = item.get("url", "N/A")
        snippet = item.get("snippet", "").strip()
        text = item.get("text", "").strip().replace("\n", " ")

        formatted += f"""Source {i}:
            - URL: {url}
            - Snippet: {snippet}
            - Text: {text}
             """
    return formatted

async def llm_normalize(query, schema, data):

    prompt = f"""You are a precise data extraction specialist. Your task is to extract and normalize structured data from the provided search results.

        QUERY: {query}
        -----------------
        SCHEMA: {schema}

        INSTRUCTIONS:
        1. Extract ONLY factual information that directly matches the query and schema requirements
        2. Return a valid JSON array containing up to 15 items maximum
        3. Each item must include ALL required fields specified in the schema
        4. Skip any items that lack required fields - do not invent missing data
        5. Prioritize diverse sources to provide comprehensive coverage
        6. Maintain data accuracy - extract exactly what is present in the source material
        7. Use consistent formatting and data types as specified in the schema
        8. If site-specific queries are involved, focus on data from those particular sources

        CRITICAL RULES:
        - Output ONLY valid JSON array format: [{{"field1":"value1", "field2":"value2"}}, ...]
        - NO additional text, explanations, or formatting markers
        - NO hallucination or assumption of missing information
        - Preserve original data accuracy and context

        Expected format: [{{"key":"value"}}, ...]"""

    try:
        formatted_data = format_sources_for_prompt(json.load(data))
        
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": formatted_data}
        ]

        if SERVICE == "GOOGLE":
            content = generate_response_google(messages=messages, model=MODEL)
        else:
            content = generate_response(messages=messages, model=MODEL)

        # Handle None content
        if content is None:
            content = "[]"
        else:
            try:
                json.loads(content)
            except Exception as e:
                # Try to extract JSON array from the content
                import re
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    cleaned_content = match.group(0)
                    try:
                        # Verify the extracted content is valid JSON
                        json.loads(cleaned_content)
                        content = cleaned_content
                    except:
                        content = "[]"
                else:
                    content = "[]"
        return content
    except Exception as e:
        print(f"[LLM Normalization Error] {e}")
        raise e

async def stream_normalization(query, schema, data):
    """Stream normalized data as Server-Sent Events using real LLM streaming"""

    prompt = f"""You are a precise data extraction specialist. Your task is to extract and normalize structured data from the provided search results.

        QUERY: {query}
        -----------------
        SCHEMA: {schema}

        INSTRUCTIONS:
        1. Extract ONLY factual information that directly matches the query and schema requirements
        2. Return a valid JSON array
        3. Each item must include ALL required fields specified in the schema
        4. Skip any items that lack required fields - do not invent missing data
        5. Prioritize diverse sources to provide comprehensive coverage
        6. Maintain data accuracy - extract exactly what is present in the source material
        7. Use consistent formatting and data types as specified in the schema
        8. If site-specific queries are involved, focus on data from those particular sources

        CRITICAL RULES:
        - Output ONLY valid JSON array format: [{{"field1":"value1", "field2":"value2"}}, ...]
        - NO additional text, explanations, or formatting markers
        - NO hallucination or assumption of missing information
        - Preserve original data accuracy and context

        Expected format: [{{"key":"value"}}, ...]"""

    try:
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": str(data)}
        ]

        if SERVICE == "GOOGLE":
            async for chunk in stream_response_google(messages=messages, model=MODEL):
                yield chunk
        else:
            async for chunk in stream_response(messages=messages, model=MODEL):
                yield chunk

    except Exception as e:
        print(f"❌ [LLM Streaming Error] {e}", flush=True)
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: DONE\n\n"
