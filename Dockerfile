FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8006
EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port $PORT"]
