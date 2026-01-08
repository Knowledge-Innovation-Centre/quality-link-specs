FROM python:3.14-slim

WORKDIR /app

RUN --mount=type=bind,source=requirements.txt,target=/app/requirements.txt pip install --no-cache-dir -r requirements.txt

ADD main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

