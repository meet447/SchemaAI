from ddgs import DDGS

def normalize(data: dict) -> dict:
    results = []
    for result in data:
        results.append({
            "title": result["title"],
            "url": result["href"],
            "snippet": result["body"]
        })
    return {
        "query": "duckduckgo",
        "results": results
    }

def ddg_search(query: str, key: str = "") -> list:
    results = DDGS().text(query, max_results=3)
    return normalize(results)
