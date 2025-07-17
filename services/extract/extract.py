from curl_cffi import requests
from services.generate.extract import requires_puppeter, extract_text_from_html

async def extract(url):

    r = requests.get(url, impersonate='chrome110')
    response = r.text
    if requires_puppeter(response):
        puppeteer_url = f"https://puppeteer-render-ig8y.onrender.com/scrape?url={url}"
        puppeteer_response = requests.get(puppeteer_url, timeout=12)
        puppeteer_response.raise_for_status()
        text = extract_text_from_html(puppeteer_response.text)
    else:
        text = extract_text_from_html(response)

    return text
