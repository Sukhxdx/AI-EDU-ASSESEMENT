# Project Overview

## Introduction

AI Edu Assessment is a comprehensive educational platform that leverages Retrieval-Augmented Generation (RAG) technology to transform how students and educators interact with educational content. The system allows users to ingest PDF documents (research papers, textbooks, etc.), ask questions about the content, and automatically generate quiz questions for assessment.

## Core Functionality

### 1. Document Ingestion
- Upload PDF documents via URL
- Automatic text extraction and processing
- Intelligent chunking that preserves semantic meaning
- Vector embedding generation for semantic search

### 2. Question Answering
- Natural language questions about ingested documents
- AI-powered answers using context from the documents
- Prevents hallucination by grounding answers in source material
- Fast response times (2-4 seconds)

### 3. Quiz Generation
- Automatic generation of multiple-choice questions
- Questions test understanding of key concepts
- Configurable number of questions (1-20)
- Topic-specific quiz generation support

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Vector Database**: Pinecone (1024-dimensional embeddings)
- **Embedding Model**: SentenceTransformers (e5-large-v2)
- **LLM**: Google Gemini 2.0 Flash / 1.5 Flash
- **Database**: SQLite (for session storage)

### Mobile
- **Framework**: React Native with Expo SDK 54
- **UI**: Custom components with modern design
- **State Management**: React Hooks
- **API Communication**: Fetch API

## Key Features

### Semantic Search
- Uses advanced embeddings for understanding meaning, not just keywords
- Finds relevant content even with different wording
- Handles synonyms and related concepts

### Context-Aware Answers
- Answers are generated from actual document content
- Reduces AI hallucination
- Provides accurate, source-grounded responses

### Intelligent Chunking
- Sentence-aware chunking preserves context
- Overlapping chunks ensure continuity
- Optimal chunk size for embedding quality

### Error Handling
- Graceful fallbacks at every stage
- User-friendly error messages
- Robust error recovery

## Use Cases

### For Students
- Study research papers with AI assistance
- Generate practice quizzes for exam preparation
- Get instant answers to questions about course material
- Understand complex concepts through Q&A

### For Educators
- Create quiz questions from course materials
- Generate assessment questions automatically
- Provide AI tutoring assistance to students
- Analyze document readability

### For Researchers
- Quickly understand research papers
- Extract key information from documents
- Generate summaries and questions
- Explore document content through queries

## System Architecture

The system follows a three-tier architecture:

1. **Presentation Layer**: React Native mobile app
2. **Application Layer**: FastAPI backend with RAG pipeline
3. **Data Layer**: Pinecone vector database + SQLite

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation.

## RAG Pipeline

The RAG pipeline is the heart of the system:

1. **Ingestion**: PDF → Text → Chunks → Embeddings → Vector DB
2. **Query**: Question → Embedding → Vector Search → Context Retrieval
3. **Generation**: Context + Question → LLM → Answer/Quiz

See [RAG_PIPELINE.md](./RAG_PIPELINE.md) for detailed pipeline documentation.

## Performance

- **PDF Ingestion**: 2-5 seconds per page
- **Query Response**: 2-4 seconds
- **Quiz Generation**: 5-10 seconds for 5 questions
- **Embedding Generation**: ~0.1 seconds per chunk

## Limitations

### Current Limitations
- Single document focus (one PDF at a time)
- No user authentication
- No document versioning
- Limited to text content (no images/tables)

### Future Enhancements
- Multi-document support
- User accounts and document libraries
- Image and table extraction
- Collaborative features
- Advanced analytics

## Getting Started

1. **Set up backend**: See [README.md](../README.md)
2. **Set up mobile app**: See [README.md](../README.md)
3. **Ingest your first PDF**: Use the mobile app
4. **Ask questions**: Try asking about the document
5. **Generate quiz**: Create assessment questions

## Documentation Structure

- **[README.md](../README.md)**: Quick start guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: System architecture details
- **[RAG_PIPELINE.md](./RAG_PIPELINE.md)**: RAG pipeline deep dive
- **[API_REFERENCE.md](./API_REFERENCE.md)**: Complete API documentation
- **[DEPLOYMENT.md](./DEPLOYMENT.md)**: Deployment guide

## Contributing

This is an educational project. Contributions are welcome! Please:
1. Read the documentation
2. Understand the architecture
3. Test your changes thoroughly
4. Follow code style guidelines

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the documentation
2. Review error messages
3. Check environment variables
4. Verify API keys are set correctly

## Acknowledgments

- **Pinecone**: Vector database infrastructure
- **Google**: Gemini LLM API
- **Hugging Face**: SentenceTransformers models
- **Expo**: React Native development platform
- **FastAPI**: Modern Python web framework

