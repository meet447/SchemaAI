import asyncio
import httpx
import sys

async def main():
    url = "http://127.0.0.1:8000/api/generate"

    query = "Upcoming Anime releases and manga releases in july"
    schema = {
        'name': "name of the product",
        'description': "description of the product",
        'release_date': "release date of the product"
    }

    headers = {
        "X-API-Key": "test",
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json={"query": query, "schema": schema, "stream": True}, headers=headers) as response:
            async for chunk in response.aiter_bytes():
                if chunk:
                    print(chunk.decode("utf-8"), end="")
                    sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())