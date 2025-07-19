import json
from core.llm import generate_response, generate_response_google
from config import SERVICE, MODEL

async def llm_normalize(schema, data):

    prompt = f"""You are a data extraction expert. Your task is to extract structured data from the provided text, which includes hyperlinks in the format "link text (URL)".
    
    WEBSITE DATA: {data}
    -----------------
    SCHEMA: {schema}
    
    INSTRUCTIONS:
    1.  **Extract Information**: Pull out data that matches the user's query and the provided schema.
    2.  **Preserve Links**: When you encounter text that includes a URL in parentheses, make sure to include the full text and the URL in the extracted data.
    3.  **Complete Items Only**: Each JSON object must have all the fields specified in the schema. Do not include items that are missing required fields.
    4.  **No Inventing Data**: Do not make up information that is not present in the text.
    5.  **Focus on Accuracy**: Extract the data exactly as it appears in the source material.
    
    CRITICAL RULES:
    - Output ONLY a valid JSON array: [{{"field1":"value1", "field2":"value2"}}, ...]
    - NO extra text, explanations, or formatting.
    
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
            content = "['error':'something went wrong']"
        else:
            try:
                json.loads(content)
            except Exception:
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
                        content = "['error':'something went wrong']"
                else:
                    content = "['error':'something went wrong']"
        return content
    except Exception as e:
        print(f"[LLM Normalization Error] {e}")
        raise e