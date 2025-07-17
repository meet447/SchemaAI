from google.genai.client import Client
import openai
from config import OPENROUTER_KEY
from google.genai import types
from config import GEMINI_API_KEY
import json
import re
import asyncio

def generate_response(messages, model):
    client = openai.OpenAI(
        base_url = "https://openrouter.ai/api/v1",
        api_key=OPENROUTER_KEY
    )

    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return completion.choices[0].message.content

def generate_response_google(messages, model):

    client = Client(api_key=GEMINI_API_KEY)
    contents = []
    system_instruction = None

    for msg in messages:
        if msg["role"] == "system":
            system_instruction = msg["content"]
            continue

        # Convert "assistant" role to "model" for the Google API
        role = "model" if msg["role"] == "assistant" else msg["role"]

        contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}] # Wrap content in 'parts'
            })

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(
                        thinking_budget=0
                    ),

        ),
    )
    return response.text

async def stream_response(messages, model):
    """Stream response from OpenRouter API"""
    client = openai.OpenAI(
        base_url = "https://openrouter.ai/api/v1",
        api_key=OPENROUTER_KEY
    )

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    collected_content = ""
    processed_length = 0

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            collected_content += content

            # Try to extract complete JSON objects as they form
            json_objects = extract_streaming_json(collected_content, processed_length)
            for json_obj, end_pos in json_objects:
                yield f"data: {json.dumps(json_obj)}\n\n"
                processed_length = end_pos
                # ✅ FIX: Give control back to the event loop to send the chunk
                await asyncio.sleep(0)


    yield "data: DONE\n\n"

async def stream_response_google(messages, model):
    """Stream response from Google Gemini API"""
    client = Client(api_key=GEMINI_API_KEY)
    contents = []
    system_instruction = None

    for msg in messages:
        if msg["role"] == "system":
            system_instruction = msg["content"]
            continue

        # Convert "assistant" role to "model" for the Google API
        role = "model" if msg["role"] == "assistant" else msg["role"]

        contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}] # Wrap content in 'parts'
            })

    response_stream = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(
                        thinking_budget=0
                    ),
        ),
    )

    collected_content = ""
    processed_length = 0

    for chunk in response_stream:
        if chunk.text:
            collected_content += chunk.text

            # Try to extract complete JSON objects as they form
            json_objects = extract_streaming_json(collected_content, processed_length)
            for json_obj, end_pos in json_objects:
                yield f"data: {json.dumps(json_obj)}\n\n"
                processed_length = end_pos
                # ✅ FIX: Give control back to the event loop to send the chunk
                await asyncio.sleep(0)


    yield "data: DONE\n\n"

def extract_json_objects(text):
    """Extract complete JSON objects from accumulated text"""
    json_objects = []

    # Try to find JSON objects in the text
    # Look for patterns like {"key": "value", ...}
    brace_count = 0
    start_pos = -1

    for i, char in enumerate(text):
        if char == '{':
            if brace_count == 0:
                start_pos = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_pos != -1:
                # Found a complete JSON object
                json_str = text[start_pos:i+1]
                try:
                    json_obj = json.loads(json_str)
                    json_objects.append(json_obj)
                except json.JSONDecodeError:
                    pass  # Invalid JSON, continue
                start_pos = -1

    return json_objects

def extract_streaming_json(text, start_pos=0):
    """Extract complete JSON objects from streaming text"""
    json_objects = []
    i = start_pos

    # Skip whitespace and array opening
    while i < len(text) and text[i] in ' \t\n\r[':
        i += 1

    while i < len(text):
        # Skip whitespace and commas
        while i < len(text) and text[i] in ' \t\n\r,':
            i += 1

        if i >= len(text):
            break

        # Look for object start
        if text[i] == '{':
            brace_count = 1
            in_string = False
            escape_next = False
            obj_start = i
            i += 1

            while i < len(text) and brace_count > 0:
                char = text[i]

                if escape_next:
                    escape_next = False
                elif char == '\\':
                    escape_next = True
                elif char == '"' and not escape_next:
                    in_string = not in_string
                elif not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1

                i += 1

            if brace_count == 0:
                # Found complete object
                json_str = text[obj_start:i]
                try:
                    json_obj = json.loads(json_str)
                    json_objects.append((json_obj, i))
                except json.JSONDecodeError:
                    pass
        else:
            # Skip to next potential object
            i += 1

    return json_objects