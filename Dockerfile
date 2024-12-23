
FROM python:3.10-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "127.0.0.`1", "--port", "8000"]
