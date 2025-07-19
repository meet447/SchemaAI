# Schemely

**Schemely** lets you turn any **natural language query** or **URL** into structured JSON data using AI-powered schema extraction.  
Just define what data you want — SchemaAI handles search, scraping, and structuring for you.

## What It Does

- Accepts search queries + desired schema → returns structured JSON
- Accepts a direct URL + schema → extracts structured data from the page
- Supports real-time **streaming** output (like ChatGPT's stream mode)
- Powered by AI + web scraping + smart schema inference

## Endpoints

### `POST /api/generate`

> Turn a **query** into structured data based on a custom schema.  
> Uses search engines, scraping, and AI to generate results.

#### Request Body

```json
{
		"query": "Upcoming anime and manga in July",
		"schema": {
				"name": "name of the product",
				"description": "description of the product",
				"release_date": "release date"
		},
		"stream": false
}
```

#### Non-Streaming Response ("stream": false)

```json
[
		{
				"name": "One Piece",
				"description": "A pirate adventure",
				"release_date": "July 1, 2023"
		},
		{
				"name": "Attack on Titan",
				"description": "Final season wrap-up",
				"release_date": "July 10, 2023"
		}
]
```

#### Streaming Response ("stream": true)

Returns a streamed response via chunked HTTP or SSE:

```
data: {"name": "Splatoon, Vol. 1", "description": "Manga (Series Debut)", "release_date": "July 22, 2025"}
data: {"name": "Splatoon, Vol. 2", "description": "Manga (Now Digital)", "release_date": "July 22, 2025"}
data: DONE
```

### `POST /api/extract`

Extract structured data from a specific URL using a schema.
has an advanced mode for **advanced schema extraction**.

#### Request Body

```json
{
		"url": "https://www.example.com/product-page",
		"schema": {
				"title": "Title of the product",
				"price": "Product price",
				"rating": "Customer rating"
		},
		"stream": false
}
```

#### Response

```json
{
		"title": "Awesome Anime Figure",
		"price": "$29.99",
		"rating": "4.8 out of 5"
}
```

## Authentication

All endpoints require an API key.

Pass your key in the X-API-Key header:

```
X-API-Key: your-api-key-here
```

## License

MIT License — open-source the core, build on top, and contribute!