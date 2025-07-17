from core.llm import generate_response_google
import ast
from engines.google import google_search
from engines.duckduckgo import ddg_search
import re
from config import SERVICE, MODEL
import asyncio

async def llm_generate_queries(high_level_prompt):
    """
    Asynchronously generates specific search queries from a high-level prompt using an LLM.
    This version cleans the LLM output and runs the blocking call in a separate thread.
    """
    prompt = f"""You are a search query optimization expert. Generate 2 distinct, highly effective search queries based on the user's request: "{high_level_prompt}"
        Guidelines:
        - Create specific, targeted queries that will yield the most relevant results
        - Use different keyword combinations and approaches for each query
        - If specific websites are mentioned, include site-specific searches
        - Optimize for search engine effectiveness (use relevant keywords, proper phrasing)
        - Ensure queries are complementary but not redundant
        - Focus on factual, searchable information
        
        Return ONLY a valid Python list format with exactly 2 string queries:
        ["specific optimized query 1", "specific optimized query 2"]"""
    try:
        messages=[{"role": "user", "content": prompt}]

        # Run the synchronous generate_response_google function in a separate thread
        # to avoid blocking the asyncio event loop.
        if SERVICE == "GOOGLE":
            content = await asyncio.to_thread(generate_response_google, messages=messages, model=MODEL)
        else:
            # Assuming generate_response is also synchronous
            from core.llm import generate_response
            content = await asyncio.to_thread(generate_response, messages=messages, model=MODEL)

        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            cleaned_content = match.group(0)
        else:
            cleaned_content = content.strip().replace('```python', '').replace('```', '')
        
        queries_list = ast.literal_eval(cleaned_content)
        if not isinstance(queries_list, list) or not all(isinstance(q, str) for q in queries_list):
            raise ValueError("LLM did not return a valid list of strings.")
        return queries_list
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing LLM response: {e}. Returning an empty list.")
        return []
    except Exception as e:
        print(f"An error occurred with the LLM API call: {e}")
        return []

async def generate_and_run_searches(high_level_prompt):
    """
    Asynchronously generates and runs search queries.
    """
    specific_queries = await llm_generate_queries(high_level_prompt)

    if not specific_queries:
        print("No queries were generated. Exiting.")
        return {}

    combined_results = {
        "google": [],
        "duckduckgo": []
    }

    # Use asyncio's default executor to run synchronous search functions concurrently
    loop = asyncio.get_running_loop()
    tasks = []

    for query in specific_queries:
        # Schedule each synchronous search function to run in the thread pool
        tasks.append(loop.run_in_executor(None, google_search, query))
        tasks.append(loop.run_in_executor(None, ddg_search, query))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    # The order of results matches the order of tasks.
    # Google results are at even indices, DDG at odd indices.
    for i, result_data in enumerate(results):
        if isinstance(result_data, Exception):
            print(f"A search task failed: {result_data}")
            continue

        if result_data and 'results' in result_data and isinstance(result_data['results'], list):
            if i % 2 == 0: # Google result
                combined_results["google"].extend(result_data['results'])
            else: # DuckDuckGo result
                combined_results["duckduckgo"].extend(result_data['results'])

    return combined_results