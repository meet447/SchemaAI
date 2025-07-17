from googlesearch import search

def normalize(data: dict) -> dict:
    results = []
    for result in data:
        results.append({
            "title": result.title,
            "url": result.url,
            "snippet": result.description
        })
    return {
        "query": "googlesearch",
        "results": results
    }

def google_search(query: str, key: str = "") -> list:
    results = list(search(query, num_results=3, unique=True, advanced=True, timeout=10))
    return normalize(results)
