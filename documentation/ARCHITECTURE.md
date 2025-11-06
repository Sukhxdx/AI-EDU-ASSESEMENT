# System Architecture

## Overview

AI Edu Assessment is a RAG (Retrieval-Augmented Generation) powered educational platform that enables users to ingest PDF documents, ask questions, and generate quizzes. The system consists of three main components:

1. **Mobile Application** (React Native/Expo)
2. **Backend API** (FastAPI)
3. **Vector Database** (Pinecone)

## Component Architecture

### 1. Mobile Application Layer

**Technology**: React Native with Expo SDK 54

**Responsibilities**:
- User interface for PDF ingestion
- Question input and answer display
- Quiz generation and display
- API communication with backend

**Key Files**:
- `mobile/App.tsx` - Main application component
- `mobile/index.js` - Entry point

**Communication**:
- Uses `fetch` API to communicate with FastAPI backend
- Environment variable `EXPO_PUBLIC_BACKEND_URL` configures backend endpoint

### 2. Backend API Layer

**Technology**: FastAPI (Python)

**Responsibilities**:
- PDF text extraction
- Text chunking and embedding generation
- Vector database operations
- LLM integration for answer generation
- Quiz question generation

**Key Components**:

#### 2.1 Main API (`backend/main.py`)
- FastAPI application setup
- CORS configuration
- Route definitions
- Request/response models

#### 2.2 RAG Pipeline (`backend/modules/rag.py`)
The core of the system, responsible for:
- PDF ingestion and text extraction
- Text chunking with sentence boundary awareness
- Embedding generation using SentenceTransformers
- Vector storage in Pinecone
- Semantic search and retrieval
- Answer generation using Gemini
- Quiz question generation

#### 2.3 Database Module (`backend/modules/db.py`)
- SQLite database operations
- Session storage and retrieval
- Legacy support for older features

### 3. Vector Database Layer

**Technology**: Pinecone (Serverless)

**Configuration**:
- Dimension: 1024 (matches e5-large-v2 embeddings)
- Metric: Cosine similarity
- Index name: Configurable (default: "nlp")

**Data Structure**:
```json
{
  "id": "doc-uuid-chunk-0",
  "values": [1024-dimensional vector],
  "metadata": {
    "text": "chunk content...",
    "doc_id": "unique-doc-id",
    "chunk_idx": 0,
    "timestamp": 1234567890,
    "source": "pdf_url"
  }
}
```

## Data Flow

### PDF Ingestion Flow

```
1. User provides PDF URL
   ↓
2. Mobile app → POST /rag/ingest
   ↓
3. Backend downloads PDF
   ↓
4. Extract text using PyPDF2
   ↓
5. Chunk text (sentence-aware, 500 words, 100 overlap)
   ↓
6. Generate embeddings (SentenceTransformers e5-large-v2)
   ↓
7. Upsert to Pinecone with metadata
   ↓
8. Return success response
```

### Question Answering Flow

```
1. User asks question
   ↓
2. Mobile app → POST /rag/query
   ↓
3. Backend embeds question (with "query:" prefix)
   ↓
4. Query Pinecone (top_k=5)
   ↓
5. Retrieve relevant chunks
   ↓
6. Build prompt with context
   ↓
7. Call Gemini API for answer generation
   ↓
8. Return formatted answer
```

### Quiz Generation Flow

```
1. User requests quiz (N questions)
   ↓
2. Mobile app → POST /rag/quiz
   ↓
3. Backend queries Pinecone for diverse contexts
   ↓
4. Retrieve top 30 chunks
   ↓
5. Deduplicate and clean contexts
   ↓
6. Build detailed prompt for Gemini
   ↓
7. Generate JSON array of questions
   ↓
8. Parse and validate questions
   ↓
9. Return quiz questions
```

## Embedding Model

**Model**: `intfloat/e5-large-v2`

**Characteristics**:
- Output dimension: 1024
- Input format: Prefix-based ("query:" or "passage:")
- Normalization: L2 normalized for cosine similarity

**Usage**:
- Passages: `"passage: {chunk_text}"`
- Queries: `"query: {question}"`

## LLM Integration

**Primary**: Google Gemini 2.0 Flash (Experimental)
**Fallback**: Google Gemini 1.5 Flash

**Configuration**:
- Temperature: 0.7
- Max tokens: 500 (answers), 2000 (quizzes)
- Timeout: 60-90 seconds

**Prompt Engineering**:
- Clear instructions for answer format
- Context limitation to prevent hallucination
- JSON structure enforcement for quizzes

## Error Handling

### Embedding Failures
- Dimension verification before upsert
- Batch processing to avoid memory issues

### LLM Failures
- Multiple endpoint fallbacks
- Graceful degradation to context-based answers
- JSON parsing with multiple extraction strategies

### Network Failures
- Retry logic in HTTP clients
- Timeout handling
- User-friendly error messages

## Scalability Considerations

### Current Limitations
- Single Pinecone index
- No document versioning
- Sequential embedding generation

### Future Improvements
- Multiple index support per user
- Document metadata filtering
- Parallel embedding generation
- Caching layer for frequent queries

## Security

### API Security
- CORS configuration for mobile app
- Environment variable for sensitive keys
- No authentication (development version)

### Data Security
- API keys stored in environment variables
- No user data persistence (except SQLite sessions)
- Vector data in Pinecone (cloud-hosted)

## Performance

### Optimization Strategies
- Batch embedding generation (32 chunks at a time)
- Batch Pinecone upserts (100 vectors at a time)
- Context length limiting (500 chars per chunk)
- Deduplication before LLM calls

### Typical Performance
- PDF ingestion: ~2-5 seconds per page
- Query response: ~2-4 seconds
- Quiz generation: ~5-10 seconds for 5 questions

