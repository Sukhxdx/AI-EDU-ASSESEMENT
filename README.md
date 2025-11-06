# AI Edu Assessment - RAG-Powered Learning Platform

A comprehensive educational assessment platform that uses Retrieval-Augmented Generation (RAG) to generate quizzes and answer questions from PDF documents. Built with FastAPI backend and React Native mobile app.

## 🎯 Features

- **PDF Ingestion**: Upload and process research papers, textbooks, and educational documents
- **Question Answering**: Ask questions about ingested documents with AI-powered answers
- **Quiz Generation**: Automatically generate multiple-choice quiz questions from document content
- **Vector Search**: Uses Pinecone for semantic search with 1024-dimensional embeddings
- **Mobile-First**: Beautiful React Native app for iOS and Android

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Mobile App │────────▶│  FastAPI     │────────▶│  Pinecone   │
│  (Expo)     │         │  Backend     │         │  Vector DB  │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ├────────▶ Gemini API (Answer Generation)
                               │
                               └────────▶ SentenceTransformers (Embeddings)
```

## 📁 Project Structure

```
AI_Edu_Assessment/
├── backend/                 # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── modules/            # Core modules
│   │   ├── rag.py         # RAG pipeline (main logic)
│   │   ├── db.py          # SQLite database
│   │   └── ...
│   ├── requirements.txt    # Python dependencies
│   └── data/              # SQLite database storage
│
├── mobile/                 # React Native app (Expo)
│   ├── App.tsx            # Main app component
│   ├── package.json       # Node dependencies
│   └── ...
│
└── documentation/          # Detailed documentation
    ├── ARCHITECTURE.md    # System architecture
    ├── RAG_PIPELINE.md    # RAG pipeline details
    └── API_REFERENCE.md   # API documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Pinecone account (free tier available)
- Gemini API key (optional but recommended)

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set environment variables** (create `backend/.env`):
   ```env
   PINECONE_API_KEY=your_pinecone_key
   GEMINI_API_KEY=your_gemini_key
   PINECONE_INDEX=nlp
   DB_PATH=data/projects.db
   ```

3. **Start the server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Mobile App Setup

1. **Install dependencies:**
   ```bash
   cd mobile
   npm install
   ```

2. **Set backend URL:**
   ```bash
   # For iOS simulator
   set EXPO_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
   
   # For real device (replace with your PC IP)
   set EXPO_PUBLIC_BACKEND_URL=http://192.168.1.22:8000
   ```

3. **Start Expo:**
   ```bash
   npx expo start --tunnel
   ```

4. **Scan QR code** with Expo Go app on your phone

## 📚 Documentation

See the [documentation/](./documentation/) folder for detailed information:

- [Architecture Overview](./documentation/ARCHITECTURE.md)
- [RAG Pipeline Details](./documentation/RAG_PIPELINE.md)
- [API Reference](./documentation/API_REFERENCE.md)
- [Deployment Guide](./documentation/DEPLOYMENT.md)

## 🔧 API Endpoints

### RAG Endpoints

- `POST /rag/ingest` - Ingest PDF from URL
- `POST /rag/query` - Ask questions about ingested documents
- `POST /rag/quiz` - Generate quiz questions

See [API_REFERENCE.md](./documentation/API_REFERENCE.md) for full details.

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python
- **Vector DB**: Pinecone (1024-dim embeddings)
- **Embeddings**: SentenceTransformers (e5-large-v2)
- **LLM**: Google Gemini 2.0 Flash / 1.5 Flash
- **Mobile**: React Native (Expo SDK 54)
- **Database**: SQLite

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read the documentation first.
