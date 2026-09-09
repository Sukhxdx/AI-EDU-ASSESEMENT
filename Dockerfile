FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ config/
COPY dataset/ dataset/
COPY models/ models/
COPY src/ src/

ENV PYTHONPATH=/app/src
EXPOSE 8501 8000

CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
