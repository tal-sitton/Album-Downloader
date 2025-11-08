FROM node:25 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the backend
FROM python:3.14-alpine AS backend-builder
RUN apk add --no-cache bash cronie

WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist /app/static

# Expose port 80
EXPOSE 80

# Start cleaner and backend
CMD python3 main.py & python3 -u clean_downloads.py > /var/log/cleaner.log  2>&1 & wait
