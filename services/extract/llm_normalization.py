import json
from core.llm import generate_response, generate_response_google
from config import SERVICE, MODEL

async def llm_normalize(schema, data):

    prompt = f"""You are a precise data extraction specialist. Your task is to extract and normalize structured data from the provided Website data.

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
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": str(data)}
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