FROM python:3.14-alpine

WORKDIR /app

RUN --mount=type=bind,source=requirements.txt,target=/app/requirements.txt pip install --no-cache-dir -r requirements.txt

RUN apk add --no-cache curl

ADD main.py .

EXPOSE 8000

HEALTHCHECK CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

