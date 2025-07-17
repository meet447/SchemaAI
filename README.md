# SchemaAI

SchemaAI lets you turn any **natural language query** or **URL** into structured JSON data using AI-powered schema extraction. Just define what data you want — SchemaAI handles search, scraping, and structuring for you.

## Endpoints

### `POST /api/generate`
> Turn a query into structured data based on a schema.

```json
{
  "query": "Upcoming anime and manga in July",
  "schema": {
    "name": "name of the product",
    "description": "description of the product",
    "release_date": "release date"
  },
  "stream": true
}