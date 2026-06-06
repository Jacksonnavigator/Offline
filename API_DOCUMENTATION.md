# REST API Documentation

## Portable Offline AI Document Reader v1.0

API for managing, scanning, searching, and analyzing documents offline using local AI models.

---

## Overview

- **Base URL**: `http://localhost:5000/api`
- **Authentication**: API Key via `X-API-Key` header
- **Response Format**: JSON
- **Content-Type**: `application/json`

---

## Authentication

All API endpoints (except `/health`) require authentication via API key header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/documents
```

**Change API key in `app_api.py`:**
```python
API_KEY = "your-secure-api-key-32-chars-minimum"
```

---

## Response Format

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed"
}
```

### Error Response
```json
{
  "error": "Error message",
  "code": 400,
  "details": {...}
}
```

---

## Endpoints

### 1. Health Check

**Endpoint**: `GET /health`  
**Auth**: None required  
**Rate Limit**: Unlimited

Check if API server is running.

```bash
curl http://localhost:5000/api/health
```

**Response** (200):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Portable Offline AI Document Reader"
}
```

---

### 2. Statistics

**Endpoint**: `GET /stats`  
**Auth**: Required  
**Rate Limit**: 30 req/min

Get application statistics and metrics.

```bash
curl -H "X-API-Key: your-key" http://localhost:5000/api/stats
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "total_documents": 42,
    "total_text_length": 1250000,
    "languages": ["en", "fr", "es"],
    "avg_ocr_confidence": 0.95,
    "database_size": "25.5 MB",
    "uptime_seconds": 3600
  }
}
```

---

### 3. List Documents

**Endpoint**: `GET /documents`  
**Auth**: Required  
**Rate Limit**: 30 req/min  
**Query Parameters**:
- `limit` (int, default: 20): Number of documents to return
- `offset` (int, default: 0): Pagination offset
- `sort` (string, default: "created_at"): Sort field
- `order` (string, default: "desc"): Ascending (asc) or descending (desc)

List all documents with pagination.

```bash
curl -H "X-API-Key: your-key" "http://localhost:5000/api/documents?limit=10&offset=0"
```

**Response** (200):
```json
{
  "success": true,
  "count": 10,
  "total": 42,
  "offset": 0,
  "documents": [
    {
      "id": 1,
      "title": "Invoice 2024",
      "content": "Invoice number INV-001...",
      "language": "en",
      "ocr_confidence": 0.96,
      "created_at": "2024-01-15T10:30:00Z",
      "image_path": "/path/to/image.jpg"
    }
  ]
}
```

---

### 4. Get Document

**Endpoint**: `GET /documents/{id}`  
**Auth**: Required  
**Rate Limit**: 60 req/min  
**Path Parameters**:
- `id` (int): Document ID

Retrieve a specific document.

```bash
curl -H "X-API-Key: your-key" http://localhost:5000/api/documents/1
```

**Response** (200):
```json
{
  "success": true,
  "document": {
    "id": 1,
    "title": "Invoice 2024",
    "content": "Full document text content...",
    "language": "en",
    "ocr_confidence": 0.96,
    "created_at": "2024-01-15T10:30:00Z",
    "image_path": "/path/to/image.jpg"
  }
}
```

**Errors**:
- 404: Document not found

---

### 5. Delete Document

**Endpoint**: `DELETE /documents/{id}`  
**Auth**: Required  
**Rate Limit**: 30 req/min

Delete a document.

```bash
curl -X DELETE -H "X-API-Key: your-key" http://localhost:5000/api/documents/1
```

**Response** (200):
```json
{
  "success": true,
  "message": "Document 1 deleted"
}
```

---

### 6. Scan Document

**Endpoint**: `POST /scan`  
**Auth**: Required  
**Rate Limit**: 30 req/min  
**Content-Type**: multipart/form-data  
**Max File Size**: 50MB

Scan and OCR an image file.

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -F "file=@document.jpg" \
  -F "title=My Document" \
  http://localhost:5000/api/scan
```

**Request**:
- `file` (file, required): Image file (JPG, PNG, etc.)
- `title` (string, optional): Document title

**Response** (200):
```json
{
  "success": true,
  "document": {
    "id": 43,
    "title": "My Document",
    "content": "Extracted text content...",
    "language": "en",
    "ocr_confidence": 0.94,
    "created_at": "2024-01-15T11:00:00Z"
  },
  "ocr_time": 12.5
}
```

---

### 7. Capture from Camera

**Endpoint**: `POST /capture`  
**Auth**: Required  
**Rate Limit**: 30 req/min  
**Content-Type**: application/json

Capture and scan from connected camera.

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"title": "Camera Scan", "frames": 5}' \
  http://localhost:5000/api/capture
```

**Request Body**:
```json
{
  "title": "Document Title",
  "frames": 5
}
```

**Response** (200):
```json
{
  "success": true,
  "document": {
    "id": 44,
    "title": "Camera Scan",
    "content": "Extracted text...",
    "language": "en",
    "ocr_confidence": 0.93,
    "created_at": "2024-01-15T11:05:00Z"
  }
}
```

---

### 8. Search Documents

**Endpoint**: `GET /search`  
**Auth**: Required  
**Rate Limit**: 30 req/min  
**Query Parameters**:
- `q` (string, required): Search query
- `limit` (int, default: 20): Max results
- `type` (string, default: "all"): search type - "keyword", "exact", "all"

Full-text search across documents.

```bash
curl -H "X-API-Key: your-key" "http://localhost:5000/api/search?q=invoice&limit=10"
```

**Response** (200):
```json
{
  "success": true,
  "query": "invoice",
  "count": 5,
  "results": [
    {
      "id": 1,
      "title": "Invoice 2024",
      "content": "Invoice number INV-001...",
      "language": "en",
      "relevance": 0.98,
      "matches": ["invoice", "INV-001"]
    }
  ]
}
```

---

### 9. Analyze Document

**Endpoint**: `POST /documents/{id}/analyze`  
**Auth**: Required  
**Rate Limit**: 30 req/min

Get AI analysis of a document.

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  http://localhost:5000/api/documents/1/analyze
```

**Response** (200):
```json
{
  "success": true,
  "analysis": {
    "document_id": 1,
    "document_type": "Invoice",
    "key_entities": {
      "amount": "$1,234.56",
      "date": "2024-01-15",
      "vendor": "ABC Corp"
    },
    "summary": "This is an invoice from ABC Corp dated 2024-01-15 for $1,234.56",
    "sentiment": "neutral",
    "confidence": 0.89
  }
}
```

---

### 10. Summarize Document

**Endpoint**: `POST /documents/{id}/summarize`  
**Auth**: Required  
**Rate Limit**: 30 req/min

Generate AI summary of document.

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  http://localhost:5000/api/documents/1/summarize
```

**Response** (200):
```json
{
  "success": true,
  "summary": "This is a concise summary of the document content in 2-3 sentences..."
}
```

---

### 11. Ask Question

**Endpoint**: `POST /documents/{id}/ask`  
**Auth**: Required  
**Rate Limit**: 30 req/min

Get AI answer to a question about document.

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total amount?"}' \
  http://localhost:5000/api/documents/1/ask
```

**Request Body**:
```json
{
  "question": "What is the main topic?"
}
```

**Response** (200):
```json
{
  "success": true,
  "answer": "Based on the document, the main topic is..."
}
```

---

### 12. Export Document

**Endpoint**: `GET /documents/{id}/export`  
**Auth**: Required  
**Rate Limit**: 30 req/min  
**Query Parameters**:
- `format` (string, required): Export format - "txt", "pdf", "docx", "md", "json"

Export document in specified format.

```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:5000/api/documents/1/export?format=pdf" \
  -o document.pdf
```

**Response** (200):
- File download (binary/appropriate content-type)

**Supported Formats**:
- `txt`: Plain text
- `pdf`: PDF document
- `docx`: Microsoft Word
- `md`: Markdown
- `json`: JSON with metadata

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Invalid/missing API key |
| 404 | Not Found | Document or endpoint not found |
| 413 | Payload Too Large | File size exceeds limit (50MB) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | Server temporarily unavailable |

---

## Rate Limiting

- **Standard endpoints**: 30 requests per minute
- **Health check**: Unlimited
- **API key based**: 100 requests per minute per key

Rate limit headers in response:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 29
X-RateLimit-Reset: 1705318260
```

---

## Examples

### Python Example
```python
import requests
import json

API_KEY = "your-api-key"
BASE_URL = "http://localhost:5000/api"
HEADERS = {"X-API-Key": API_KEY}

# Get documents
response = requests.get(f"{BASE_URL}/documents", headers=HEADERS)
docs = response.json()
print(f"Found {docs['count']} documents")

# Search
response = requests.get(
    f"{BASE_URL}/search",
    params={"q": "invoice"},
    headers=HEADERS
)
results = response.json()
print(f"Search found {results['count']} matches")

# Analyze
response = requests.post(
    f"{BASE_URL}/documents/1/analyze",
    headers=HEADERS
)
analysis = response.json()
print(f"Analysis: {analysis['analysis']}")

# Upload file
files = {"file": open("document.jpg", "rb")}
data = {"title": "My Document"}
response = requests.post(
    f"{BASE_URL}/scan",
    files=files,
    data=data,
    headers=HEADERS
)
print(f"Created document: {response.json()['document']['id']}")
```

### JavaScript Example
```javascript
const API_KEY = "your-api-key";
const BASE_URL = "http://localhost:5000/api";
const HEADERS = { "X-API-Key": API_KEY };

// Get documents
async function getDocuments() {
  const response = await fetch(`${BASE_URL}/documents`, { headers: HEADERS });
  const data = await response.json();
  console.log(`Found ${data.count} documents`);
}

// Search
async function searchDocuments(query) {
  const response = await fetch(
    `${BASE_URL}/search?q=${encodeURIComponent(query)}`,
    { headers: HEADERS }
  );
  const data = await response.json();
  console.log(`Found ${data.count} results`);
}

// Upload file
async function uploadDocument(file, title) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", title);
  
  const response = await fetch(`${BASE_URL}/scan`, {
    method: "POST",
    headers: HEADERS,
    body: formData
  });
  
  const data = await response.json();
  console.log(`Document created: ${data.document.id}`);
}
```

### Bash/cURL Example
```bash
#!/bin/bash

API_KEY="your-api-key"
BASE_URL="http://localhost:5000/api"

# Health check
curl "$BASE_URL/health"

# Get documents
curl -H "X-API-Key: $API_KEY" "$BASE_URL/documents"

# Search
curl -H "X-API-Key: $API_KEY" "$BASE_URL/search?q=invoice"

# Scan file
curl -X POST \
  -H "X-API-Key: $API_KEY" \
  -F "file=@document.jpg" \
  -F "title=My Document" \
  "$BASE_URL/scan"

# Export
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/documents/1/export?format=pdf" \
  -o document.pdf
```

---

## Pagination

For list endpoints, use `limit` and `offset`:

```bash
# Get documents 1-10
curl -H "X-API-Key: key" "http://localhost:5000/api/documents?limit=10&offset=0"

# Get documents 11-20
curl -H "X-API-Key: key" "http://localhost:5000/api/documents?limit=10&offset=10"
```

---

## Filtering & Sorting

Supported on list endpoints:

```bash
# Sort by creation date (descending)
curl -H "X-API-Key: key" "http://localhost:5000/api/documents?sort=created_at&order=desc"

# Sort by title (ascending)
curl -H "X-API-Key: key" "http://localhost:5000/api/documents?sort=title&order=asc"
```

---

## Performance Tips

1. **Batch requests**: Group multiple operations
2. **Cache results**: Store frequently accessed data
3. **Use pagination**: Limit result sizes
4. **Compress responses**: Enable gzip compression
5. **Monitor rate limits**: Stay within limits
6. **Use appropriate endpoints**: Choose most efficient call

---

## Support & Feedback

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Email**: support@example.com

---

**API Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Status**: Production Ready
