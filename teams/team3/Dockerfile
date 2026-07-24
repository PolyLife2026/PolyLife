# Team team3 — backend image.  *** REPLACE WITH YOUR OWN STACK ***
# Build your service so it listens on port 8000 and serves both your UI (/)
# and your API (/api/...). It reads the trusted X-User-* headers the gateway
# injects, and connects to its own database via DATABASE_URL (from .env).
#
# Minimal Django starting point (uncomment and flesh out):
# FROM python:3.12-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# EXPOSE 8000
# CMD ["gunicorn", "yourproject.wsgi:application", "-b", "0.0.0.0:8000"]
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000"]