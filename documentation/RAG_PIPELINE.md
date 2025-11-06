# RAG Pipeline Deep Dive

## Overview

The RAG (Retrieval-Augmented Generation) pipeline is the core component of the AI Edu Assessment system. It enables semantic search over document content and generates contextually accurate answers and quiz questions.

## Pipeline Components

### 1. Document Ingestion

#### PDF Text Extraction
```python
def _extract_text_from_pdf_url(pdf_url: str) -> str
```

**Process**:
1. Downloads PDF from URL using `httpx`
2. Uses `PyPDF2` to extract text from each page
3. Combines all pages into a single text string
4. Handles redirects and errors gracefully

**Challenges**:
- PDF formatting issues
- Multi-column layouts
- Images and tables (not extracted)

#### Text Chunking

```python
def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]
```

**Strategy**: Sentence-aware chunking

**Algorithm**:
1. Split text by sentence boundaries (`.`, `!`, `?`)
2. Build chunks by adding sentences until reaching `chunk_size` words
3. Maintain `overlap` sentences between chunks for context continuity
4. Filter out chunks with less than 20 words

**Why Sentence-Aware?**
- Preserves semantic meaning
- Avoids breaking concepts mid-sentence
- Better embedding quality

**Parameters**:
- `chunk_size`: 500 words (optimal for e5-large-v2)
- `overlap`: 100 words (ensures context continuity)

### 2. Embedding Generation

#### Model Selection

**Model**: `intfloat/e5-large-v2`
- **Dimensions**: 1024
- **Type**: Dense embeddings
- **Normalization**: L2 normalized
- **Format**: Prefix-based ("query:" or "passage:")

#### Embedding Process

```python
passages = [f"passage: {chunk}" for chunk in chunks]
vectors = embedder.encode(passages, normalize_embeddings=True)
```

**Key Points**:
- Prefix "passage:" is required for document chunks
- Prefix "query:" is required for questions
- Normalization ensures cosine similarity works correctly
- Batch processing (32 at a time) for memory efficiency

#### Vector Verification

Before upserting to Pinecone:
- Verify dimension is exactly 1024
- Check for NaN or infinite values
- Ensure all vectors are normalized

### 3. Vector Storage (Pinecone)

#### Index Configuration

```python
index = pc.create_index(
    name="nlp",
    dimension=1024,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)
```

**Why Cosine Similarity?**
- Works well with normalized embeddings
- Measures semantic similarity effectively
- Standard for text embeddings

#### Data Structure

Each vector in Pinecone contains:

```json
{
  "id": "doc-abc123-chunk-0",
  "values": [1024 float values],
  "metadata": {
    "text": "Actual chunk text (max 1000 chars)",
    "doc_id": "abc123",
    "chunk_idx": 0,
    "timestamp": 1234567890,
    "source": "https://arxiv.org/pdf/..."
  }
}
```

**ID Strategy**:
- Format: `{doc_id}-chunk-{index}`
- Ensures uniqueness across multiple documents
- Allows document-level operations

#### Upsert Process

1. Batch vectors (100 at a time)
2. Include metadata for retrieval
3. Handle errors gracefully
4. Return count of successfully upserted vectors

### 4. Query Processing

#### Question Embedding

```python
query_embedding = embedder.encode([f"query: {question}"], normalize_embeddings=True)
```

**Important**: Must use "query:" prefix for proper semantic matching.

#### Semantic Search

```python
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)
```

**Parameters**:
- `top_k`: Number of relevant chunks to retrieve (default: 5)
- `include_metadata`: Returns chunk text for context

**Retrieval Strategy**:
- Cosine similarity ranking
- Returns most semantically similar chunks
- Not keyword-based (semantic understanding)

### 5. Answer Generation

#### Context Preparation

```python
contexts = [result["metadata"]["text"] for result in results["matches"]]
clean_contexts = [clean_and_limit(ctx) for ctx in contexts[:5]]
```

**Cleaning Process**:
- Remove excessive whitespace
- Limit to 300 characters per context
- Combine top 5 contexts

#### Prompt Engineering

```
You are a helpful educational assistant. Answer the question based ONLY on the provided context.

Question: {user_question}

Context from document:
{cleaned_contexts}

Instructions:
- Provide a clear, concise answer in 2-4 sentences
- Use only information from the context provided
- If the context doesn't contain enough information, say so
- Format your answer in plain text, no markdown

Answer:
```

**Key Design Decisions**:
- Explicit instruction to use only context (prevents hallucination)
- Length constraint (2-4 sentences)
- Plain text output (no markdown)

#### LLM Integration

**Primary**: Gemini 2.0 Flash Experimental
**Fallback**: Gemini 1.5 Flash

**Configuration**:
```python
{
    "temperature": 0.7,  # Balanced creativity/accuracy
    "maxOutputTokens": 500  # Sufficient for 2-4 sentences
}
```

**Error Handling**:
- Try primary endpoint first
- Fallback to secondary endpoint
- If both fail, return context-based summary

### 6. Quiz Generation

#### Context Retrieval

```python
# Query for diverse contexts
query = "query: main concepts and key information"
results = index.query(vector=embed(query), top_k=30)
```

**Strategy**:
- Retrieve more contexts (30) for diversity
- Use generic query to get varied content
- Deduplicate similar contexts

#### Question Generation Prompt

```
You are an expert quiz creator. Generate exactly {N} high-quality multiple-choice quiz questions.

Content:
{contexts}

Requirements:
- Each question should test understanding of key concepts
- Provide 4 multiple choice options (A, B, C, D)
- Make questions clear and specific
- Ensure correct answers are accurate based on content
- Return ONLY a valid JSON array

Format:
[
  {"question": "...", "choices": ["...", "...", "...", "..."], "correct": "A"},
  ...
]
```

#### JSON Parsing

**Challenges**:
- LLM may add markdown code blocks
- May include explanatory text
- JSON may be malformed

**Solution**:
1. Extract JSON from markdown blocks if present
2. Find first `[` and last `]`
3. Parse JSON with error handling
4. Validate structure
5. Clean and normalize

**Validation**:
- Check for required fields (question, choices, correct)
- Ensure choices is a list with 2-4 items
- Normalize correct answer to uppercase

## Performance Optimization

### Batch Processing

**Embeddings**: Process 32 chunks at a time
- Prevents memory overflow
- Maintains reasonable speed

**Pinecone Upserts**: 100 vectors per batch
- Optimal for API limits
- Faster than individual upserts

### Context Limiting

- Chunk size: 500 words (optimal for embeddings)
- Context per answer: 5 chunks, 300 chars each
- Context per quiz: 10 chunks, 500 chars each

### Caching Opportunities

- Embedding cache (same chunks)
- Query result cache (same questions)
- Quiz generation cache (same document)

## Error Handling

### Embedding Errors
- Dimension mismatch → Return error
- Model loading failure → Raise exception
- Encoding errors → Skip problematic chunks

### Pinecone Errors
- Index not found → Create index
- Upsert failures → Retry with smaller batches
- Query failures → Return empty results

### LLM Errors
- API failures → Try fallback endpoint
- Timeout → Return context summary
- Invalid JSON → Use fallback questions

## Future Improvements

1. **Hybrid Search**: Combine semantic + keyword search
2. **Reranking**: Use cross-encoder for better relevance
3. **Multi-document**: Support querying across multiple PDFs
4. **Citation**: Include source chunks in answers
5. **Streaming**: Stream answers as they're generated
6. **Fine-tuning**: Fine-tune embeddings on educational content

