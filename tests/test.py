import requests

url = "http://127.0.0.1:8000/api/generate"

query = "Upcoming Anime releases and manga releases in july"

schema = {
    'name':"name of the product",
    'description':"description of the product",
    'release_date':"release date of the product"
}

response = requests.post(url, json={"query": query, "schema": schema}, headers={"X-API-Key": "test"})

print(response.json())
