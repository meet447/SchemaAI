import asyncio
from bs4 import BeautifulSoup
from curl_cffi import AsyncSession # Import the asynchronous client
import re

def requires_puppeter(response_text, min_length=200):
    soup = BeautifulSoup(response_text, "html.parser")

    # Extract and clean visible text
    text = soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text)

    # Heuristics to decide if Puppeteer/Selenium is needed
    if len(text) < min_length:
        return True

    if re.search(r'enable javascript|loading|please wait|captcha|cloudflare', text, re.I):
        return True

    # Many <script> tags, no real content
    if len(soup.find_all("script")) > 10 and len(text) < 150:
        return True

    return False

def check_duplicate_url(data):
    """
    Correctly parses the search result data, deduplicates by URL,
    and returns a list of unique site information dictionaries.
    (This function remains synchronous as it is CPU-bound)
    """
    seen_urls = set()
    unique_results = []
    for results_list in data.values():
        if isinstance(results_list, list):
            for result in results_list:
                if isinstance(result, dict) and 'url' in result and result['url']:
                    url = result['url']
                    if url not in seen_urls:
                        seen_urls.add(url)
                        unique_results.append(result)
    return unique_results

def extract_text_from_html(html_content):
    """
    Extracts and cleans text from HTML content using BeautifulSoup.
    (This function also remains synchronous)
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements for faster processing
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()

    text = soup.get_text().strip()

    # Limit text length for faster processing (first 3000 chars)
    if len(text) > 6000:
        text = text[:6000]

    # Remove newlines and replace with spaces
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    # Remove other control characters and keep only printable characters
    text = ''.join(char for char in text if char.isprintable() or char.isspace())

    # Normalize multiple spaces to single spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


async def fetch_and_process(client, site_info):
    """
    Asynchronously fetches a single URL, extracts text, and returns the result.
    """
    site_url = site_info.get('url')
    site_snippet = site_info.get('snippet', '') # Default to empty string

    if not site_url:
        return None

    try:
        # Use the async client to make a non-blocking request
        response = await client.get(site_url, timeout=3, impersonate="chrome131")
        response.raise_for_status()

        # Check if the content requires puppeteer
        if requires_puppeter(response.text):
            puppeteer_url = f"https://puppeteer-render-ig8y.onrender.com/scrape?url={site_url}"
            puppeteer_response = await client.get(puppeteer_url, timeout=12)
            puppeteer_response.raise_for_status()
            text = extract_text_from_html(puppeteer_response.text)
        else:
            text = extract_text_from_html(response.text)

        return {
            "url": site_url,
            "text": text,
            "snippet": site_snippet
        }
    except Exception as e:
        return None # Return None on failure


async def extract(sites, max_concurrent=5):
    """
    Asynchronously fetches website content in parallel after deduplicating URLs.
    """
    sites_to_fetch = check_duplicate_url(sites)

    # Use an AsyncClient session to manage connections efficiently
    async with AsyncSession() as client:
        # Create a list of tasks (coroutines) to be executed
        tasks = [fetch_and_process(client, site_info) for site_info in sites_to_fetch]

        # Run all tasks concurrently and wait for them to complete
        results = await asyncio.gather(*tasks)

    # Filter out any None results from failed requests
    return [result for result in results if result is not None]
