# Deployment Guide

## Backend Deployment

### Option 1: Local Development

**Requirements**:
- Python 3.10+
- Virtual environment

**Steps**:

1. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   Create `backend/.env`:
   ```env
   PINECONE_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   PINECONE_INDEX=nlp
   DB_PATH=data/projects.db
   ```

4. **Run server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Option 2: Using ngrok (For Mobile Testing)

1. **Start backend** (as above)

2. **Install ngrok**:
   ```bash
   # Download from https://ngrok.com/
   ```

3. **Expose backend**:
   ```bash
   ngrok http 8000
   ```

4. **Use ngrok URL** in mobile app:
   ```env
   EXPO_PUBLIC_BACKEND_URL=https://your-ngrok-url.ngrok.io
   ```

### Option 3: Cloud Deployment (Recommended for Production)

#### Using Railway

1. **Create Railway account** at https://railway.app

2. **Create new project** and connect GitHub repo

3. **Set environment variables** in Railway dashboard:
   - `PINECONE_API_KEY`
   - `GEMINI_API_KEY`
   - `PINECONE_INDEX`
   - `DB_PATH`

4. **Deploy**: Railway auto-detects Python and deploys

#### Using Render

1. **Create Render account** at https://render.com

2. **Create new Web Service**

3. **Configure**:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3

4. **Set environment variables** in Render dashboard

## Mobile App Deployment

### Development (Expo Go)

1. **Install Expo Go** on your phone (iOS/Android)

2. **Start development server**:
   ```bash
   cd mobile
   npm install
   npx expo start --tunnel
   ```

3. **Scan QR code** with Expo Go app

### Production Build

#### iOS

1. **Install EAS CLI**:
   ```bash
   npm install -g eas-cli
   ```

2. **Configure**:
   ```bash
   eas build:configure
   ```

3. **Build**:
   ```bash
   eas build --platform ios
   ```

4. **Submit to App Store**:
   ```bash
   eas submit --platform ios
   ```

#### Android

1. **Build APK/AAB**:
   ```bash
   eas build --platform android
   ```

2. **Submit to Play Store**:
   ```bash
   eas submit --platform android
   ```

## Environment Variables

### Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `PINECONE_API_KEY` | Yes | Pinecone API key |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `PINECONE_INDEX` | No | Index name (default: "nlp") |
| `DB_PATH` | No | SQLite database path |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |

### Mobile

| Variable | Required | Description |
|----------|----------|-------------|
| `EXPO_PUBLIC_BACKEND_URL` | Yes | Backend API URL |

## Production Checklist

### Backend
- [ ] Set all required environment variables
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Add authentication/authorization
- [ ] Set up monitoring/logging
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Enable error tracking (Sentry, etc.)

### Mobile
- [ ] Update `EXPO_PUBLIC_BACKEND_URL` to production URL
- [ ] Test on real devices
- [ ] Optimize bundle size
- [ ] Add error tracking
- [ ] Test offline scenarios
- [ ] Submit to app stores

## Monitoring

### Backend Monitoring

Consider using:
- **Sentry**: Error tracking
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Logtail**: Log aggregation

### Mobile Monitoring

- **Expo Analytics**: Built-in analytics
- **Sentry React Native**: Error tracking
- **Firebase Analytics**: User analytics

## Scaling Considerations

### Backend
- Use load balancer for multiple instances
- Implement caching (Redis)
- Use connection pooling for database
- Consider async task queue (Celery) for long operations

### Vector Database
- Pinecone handles scaling automatically
- Consider multiple indexes for different document types
- Monitor index size and performance

## Security

### API Security
- Add API key authentication
- Implement rate limiting
- Use HTTPS only
- Validate all inputs
- Sanitize outputs

### Data Security
- Encrypt sensitive data
- Use secure environment variable storage
- Implement proper access controls
- Regular security audits

## Troubleshooting

### Backend won't start
- Check Python version (3.10+)
- Verify all dependencies installed
- Check environment variables
- Review error logs

### Mobile app can't connect
- Verify backend URL is correct
- Check CORS settings
- Ensure backend is accessible from device
- Try tunnel mode in Expo

### Embeddings not working
- Verify Pinecone API key
- Check index exists
- Verify embedding dimension (1024)
- Check model downloads correctly

### Quiz generation fails
- Ensure PDF is ingested first
- Check Gemini API key
- Verify sufficient contexts retrieved
- Check JSON parsing logic

