from curl_cffi import requests
from services.generate.extract import requires_puppeter
from bs4 import BeautifulSoup
import re

def extract_text_with_links_from_html(html_content):
    """
    Extracts cleaned text from HTML content and preserves hyperlinks.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()

    # Find all links and append their href to the link text
    for a in soup.find_all('a', href=True):
        if a.string:
            a.string.replace_with(f"{a.string.strip()} ({a['href']})")

    text = soup.get_text().strip()

    # Clean up whitespace
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text).strip()

    return text

async def extract(url, advanced):

    r = requests.get(url, impersonate='chrome110')
    response = r.text
    
    if advanced:
        puppeteer_url = f"https://puppeteer-render-ig8y.onrender.com/scrape?url={url}"
        puppeteer_response = requests.get(puppeteer_url, timeout=12)
        puppeteer_response.raise_for_status()
        text = extract_text_with_links_from_html(puppeteer_response.text)
        
    elif requires_puppeter(response):
        puppeteer_url = f"https://puppeteer-render-ig8y.onrender.com/scrape?url={url}"
        puppeteer_response = requests.get(puppeteer_url, timeout=12)
        puppeteer_response.raise_for_status()
        text = extract_text_with_links_from_html(puppeteer_response.text)
    else:
        text = extract_text_with_links_from_html(response)

    return text
