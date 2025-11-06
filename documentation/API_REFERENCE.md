# API Reference

## Base URL

```
http://localhost:8000
```

Or your deployed backend URL.

## Authentication

Currently, no authentication is required. API keys are managed server-side via environment variables.

## Endpoints

### Health Check

#### `GET /health`

Check if the API is running.

**Response**:
```json
{
  "status": "ok"
}
```

---

### RAG Endpoints

#### `POST /rag/ingest`

Ingest a PDF document from a URL into the vector database.

**Request Body**:
```json
{
  "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
  "index_name": "nlp"  // Optional, defaults to env var
}
```

**Response**:
```json
{
  "added": 45,
  "doc_id": "abc12345",
  "chunks": 45
}
```

**Error Response**:
```json
{
  "detail": "Error message"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://arxiv.org/pdf/1706.03762.pdf"}'
```

---

#### `POST /rag/query`

Ask a question about ingested documents.

**Request Body**:
```json
{
  "question": "What is attention mechanism?",
  "top_k": 5,  // Optional, default: 5
  "index_name": "nlp"  // Optional
}
```

**Response**:
```json
{
  "answer": "The attention mechanism is a component that allows...",
  "contexts": [
    "Context chunk 1...",
    "Context chunk 2...",
    ...
  ]
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "top_k": 5}'
```

---

#### `POST /rag/quiz`

Generate quiz questions from ingested documents.

**Request Body**:
```json
{
  "num_questions": 5,  // Optional, default: 5
  "topic": "attention mechanism",  // Optional, for topic-specific questions
  "index_name": "nlp"  // Optional
}
```

**Response**:
```json
{
  "questions": [
    {
      "question": "What is the main innovation of the Transformer architecture?",
      "choices": [
        "Self-attention mechanism",
        "Recurrent connections",
        "Convolutional layers",
        "Pooling operations"
      ],
      "correct": "A"
    },
    ...
  ],
  "count": 5
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/rag/quiz \
  -H "Content-Type: application/json" \
  -d '{"num_questions": 5}'
```

---

### Legacy Endpoints (Optional)

These endpoints are from the original implementation and may not be actively used:

#### `POST /analyze`

Analyze text for readability, generate glossary, and create quizzes.

**Request Body**:
```json
{
  "text": "Your text here...",
  "language": "en",
  "num_questions": 5
}
```

#### `GET /sessions`

List all saved sessions.

#### `GET /sessions/{id}`

Retrieve a specific session by ID.

---

## Error Codes

### 400 Bad Request
- Missing required fields
- Invalid request format
- Empty PDF content

### 404 Not Found
- Session not found
- Index not found

### 500 Internal Server Error
- Embedding generation failure
- Pinecone API error
- LLM API error
- Database error

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting for production use.

## Best Practices

### PDF URLs
- Use direct PDF links (not HTML pages)
- Ensure PDFs are publicly accessible
- Recommended: arXiv PDFs, research paper repositories

### Questions
- Ask specific, focused questions
- Avoid overly broad questions
- Questions work best when related to the ingested document

### Quiz Generation
- Ingest PDF first before generating quiz
- Use 3-10 questions for best results
- Topic parameter helps focus on specific areas

## Response Times

Typical response times:
- `/rag/ingest`: 2-10 seconds (depends on PDF size)
- `/rag/query`: 2-4 seconds
- `/rag/quiz`: 5-15 seconds (depends on number of questions)

## Testing

Use the interactive API docs at:
```
http://localhost:8000/docs
```

This provides a Swagger UI for testing all endpoints.

