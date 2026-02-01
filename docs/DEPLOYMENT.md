# ApexTrade - Deployment Guide

**Version:** 1.0  
**Date:** February 1, 2026  
**Environment:** Docker + Docker Compose

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Docker Compose Setup](#3-docker-compose-setup)
4. [Environment Configuration](#4-environment-configuration)
5. [Service Configuration](#5-service-configuration)
6. [SSL/TLS Configuration](#6-ssltls-configuration)
7. [Monitoring Setup](#7-monitoring-setup)
8. [Backup & Recovery](#8-backup--recovery)
9. [Production Checklist](#9-production-checklist)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Overview

### 1.1 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEPLOYMENT TOPOLOGY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         DOCKER HOST                                  │   │
│   │                                                                      │   │
│   │  ┌──────────────────────────────────────────────────────────────┐   │   │
│   │  │                    Docker Network: apextrade                  │   │   │
│   │  │                                                               │   │   │
│   │  │   ┌─────────────┐                                             │   │   │
│   │  │   │   Nginx     │ :80, :443                                   │   │   │
│   │  │   │ (Reverse    │                                             │   │   │
│   │  │   │  Proxy)     │                                             │   │   │
│   │  │   └──────┬──────┘                                             │   │   │
│   │  │          │                                                    │   │   │
│   │  │    ┌─────┴─────┐                                              │   │   │
│   │  │    │           │                                              │   │   │
│   │  │    ▼           ▼                                              │   │   │
│   │  │  ┌───────┐   ┌───────┐                                        │   │   │
│   │  │  │Frontend│  │ API   │                                        │   │   │
│   │  │  │:3000   │  │:8000  │                                        │   │   │
│   │  │  └───────┘  └───┬───┘                                         │   │   │
│   │  │                  │                                             │   │   │
│   │  │    ┌─────────────┼─────────────┐                              │   │   │
│   │  │    │             │             │                               │   │   │
│   │  │    ▼             ▼             ▼                               │   │   │
│   │  │  ┌───────┐   ┌───────┐   ┌───────┐                            │   │   │
│   │  │  │Redis  │   │Postgres│  │Celery │                            │   │   │
│   │  │  │:6379  │   │:5432   │  │Worker │                            │   │   │
│   │  │  └───────┘   └───────┘  └───────┘                             │   │   │
│   │  │                                                               │   │   │
│   │  │  ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐               │   │   │
│   │  │  │Timescale   │MinIO  │   │Grafana│   │Prometheus│            │   │   │
│   │  │  │:5433  │   │:9000  │   │:3001  │   │:9090  │               │   │   │
│   │  │  └───────┘   └───────┘   └───────┘   └───────┘               │   │   │
│   │  │                                                               │   │   │
│   │  └───────────────────────────────────────────────────────────────┘   │   │
│   │                                                                      │   │
│   │  Volumes:                                                            │   │
│   │  • postgres_data    • redis_data    • minio_data                    │   │
│   │  • timescale_data   • grafana_data  • prometheus_data               │   │
│   │                                                                      │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Container Summary

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| nginx | nginx:alpine | 80, 443 | Reverse proxy, SSL termination |
| frontend | node:20-alpine | 3000 | Next.js application |
| api | python:3.11-slim | 8000 | FastAPI backend |
| celery_worker | python:3.11-slim | - | Background tasks |
| celery_beat | python:3.11-slim | - | Scheduled tasks |
| postgres | postgres:16-alpine | 5432 | Main database |
| timescaledb | timescale/timescaledb:latest-pg16 | 5433 | Time-series data |
| redis | redis:7-alpine | 6379 | Cache, message broker |
| minio | minio/minio:latest | 9000, 9001 | Object storage |
| prometheus | prom/prometheus:latest | 9090 | Metrics collection |
| grafana | grafana/grafana-oss:latest | 3001 | Dashboards |
| loki | grafana/loki:latest | 3100 | Log aggregation |

---

## 2. Prerequisites

### 2.1 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Storage | 50 GB SSD | 200+ GB SSD |
| OS | Ubuntu 22.04+ / Debian 12+ | Ubuntu 24.04 LTS |

### 2.2 Required Software

```bash
# Check Docker version
docker --version  # Requires 24.0+

# Check Docker Compose version
docker compose version  # Requires 2.20+

# Install Docker (Ubuntu)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 2.3 Domain & Network

- Domain name pointing to server IP
- Ports 80 and 443 open for HTTP/HTTPS
- Port 22 open for SSH (restricted IP)
- Firewall configured (UFW or iptables)

---

## 3. Docker Compose Setup

### 3.1 Main docker-compose.yml

```yaml
# docker-compose.yml
version: '3.9'

services:
  # ============================================
  # REVERSE PROXY
  # ============================================
  nginx:
    image: nginx:alpine
    container_name: apextrade-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - frontend
      - api
    networks:
      - apextrade
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================
  # FRONTEND
  # ============================================
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: apextrade-frontend
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL}
    expose:
      - "3000"
    networks:
      - apextrade
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================
  # BACKEND API
  # ============================================
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: apextrade-api
    restart: unless-stopped
    env_file:
      - .env
    expose:
      - "8000"
    depends_on:
      postgres:
        condition: service_healthy
      timescaledb:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - apextrade
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  # ============================================
  # CELERY WORKERS
  # ============================================
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.celery
    container_name: apextrade-celery-worker
    restart: unless-stopped
    command: celery -A app.celery worker --loglevel=info --concurrency=4
    env_file:
      - .env
    depends_on:
      - api
      - redis
    networks:
      - apextrade
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.celery
    container_name: apextrade-celery-beat
    restart: unless-stopped
    command: celery -A app.celery beat --loglevel=info
    env_file:
      - .env
    depends_on:
      - redis
    networks:
      - apextrade

  celery_flower:
    image: mher/flower:latest
    container_name: apextrade-flower
    restart: unless-stopped
    command: celery --broker=${CELERY_BROKER_URL} flower --port=5555
    environment:
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    expose:
      - "5555"
    depends_on:
      - redis
    networks:
      - apextrade

  # ============================================
  # DATABASES
  # ============================================
  postgres:
    image: postgres:16-alpine
    container_name: apextrade-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    expose:
      - "5432"
    networks:
      - apextrade
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 2G

  timescaledb:
    image: timescale/timescaledb:latest-pg16
    container_name: apextrade-timescaledb
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${TIMESCALE_USER}
      - POSTGRES_PASSWORD=${TIMESCALE_PASSWORD}
      - POSTGRES_DB=${TIMESCALE_DB}
    volumes:
      - timescale_data:/var/lib/postgresql/data
      - ./scripts/init-timescale.sql:/docker-entrypoint-initdb.d/init.sql:ro
    expose:
      - "5432"
    ports:
      - "5433:5432"
    networks:
      - apextrade
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${TIMESCALE_USER} -d ${TIMESCALE_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 4G

  # ============================================
  # CACHE & MESSAGE BROKER
  # ============================================
  redis:
    image: redis:7-alpine
    container_name: apextrade-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    expose:
      - "6379"
    networks:
      - apextrade
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 1G

  # ============================================
  # OBJECT STORAGE
  # ============================================
  minio:
    image: minio/minio:latest
    container_name: apextrade-minio
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
    volumes:
      - minio_data:/data
    expose:
      - "9000"
      - "9001"
    networks:
      - apextrade
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================
  # MONITORING
  # ============================================
  prometheus:
    image: prom/prometheus:latest
    container_name: apextrade-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./monitoring/prometheus/rules:/etc/prometheus/rules:ro
      - prometheus_data:/prometheus
    expose:
      - "9090"
    networks:
      - apextrade

  grafana:
    image: grafana/grafana-oss:latest
    container_name: apextrade-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=${GRAFANA_ROOT_URL}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro
    expose:
      - "3000"
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
    networks:
      - apextrade

  loki:
    image: grafana/loki:latest
    container_name: apextrade-loki
    restart: unless-stopped
    command: -config.file=/etc/loki/loki.yml
    volumes:
      - ./monitoring/loki/loki.yml:/etc/loki/loki.yml:ro
      - loki_data:/loki
    expose:
      - "3100"
    networks:
      - apextrade

  promtail:
    image: grafana/promtail:latest
    container_name: apextrade-promtail
    restart: unless-stopped
    command: -config.file=/etc/promtail/promtail.yml
    volumes:
      - ./monitoring/promtail/promtail.yml:/etc/promtail/promtail.yml:ro
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    depends_on:
      - loki
    networks:
      - apextrade

# ============================================
# NETWORKS
# ============================================
networks:
  apextrade:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

# ============================================
# VOLUMES
# ============================================
volumes:
  postgres_data:
    driver: local
  timescale_data:
    driver: local
  redis_data:
    driver: local
  minio_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
  loki_data:
    driver: local
```

### 3.2 Development Override

```yaml
# docker-compose.override.yml (for development)
version: '3.9'

services:
  frontend:
    build:
      target: development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    command: npm run dev

  api:
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - DEBUG=true

  postgres:
    ports:
      - "5432:5432"

  redis:
    ports:
      - "6379:6379"

  minio:
    ports:
      - "9000:9000"
      - "9001:9001"
```

### 3.3 Dockerfiles

**Backend Dockerfile:**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base

WORKDIR /app

# Install dependencies
FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

# Development stage
FROM base AS development
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Build stage
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Production stage
FROM base AS production
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

---

## 4. Environment Configuration

### 4.1 Environment File Template

```bash
# .env.example

# ============================================
# APPLICATION
# ============================================
APP_NAME=ApexTrade
APP_ENV=production
DEBUG=false
SECRET_KEY=your-super-secret-key-change-in-production
ALLOWED_HOSTS=apextrade.example.com,localhost

# ============================================
# DATABASE - POSTGRESQL
# ============================================
POSTGRES_USER=apextrade
POSTGRES_PASSWORD=secure-password-here
POSTGRES_DB=apextrade
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# ============================================
# DATABASE - TIMESCALEDB
# ============================================
TIMESCALE_USER=apextrade_ts
TIMESCALE_PASSWORD=secure-password-here
TIMESCALE_DB=apextrade_ts
TIMESCALE_HOST=timescaledb
TIMESCALE_PORT=5432
TIMESCALE_URL=postgresql+asyncpg://${TIMESCALE_USER}:${TIMESCALE_PASSWORD}@${TIMESCALE_HOST}:${TIMESCALE_PORT}/${TIMESCALE_DB}

# ============================================
# REDIS
# ============================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=secure-password-here
REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/0
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/1

# ============================================
# MINIO (S3-COMPATIBLE STORAGE)
# ============================================
MINIO_ROOT_USER=apextrade
MINIO_ROOT_PASSWORD=secure-password-here
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=${MINIO_ROOT_USER}
MINIO_SECRET_KEY=${MINIO_ROOT_PASSWORD}
MINIO_BUCKET=apextrade-data
MINIO_SECURE=false

# ============================================
# JWT AUTHENTICATION
# ============================================
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# ENCRYPTION (API KEYS)
# ============================================
ENCRYPTION_KEY=your-32-byte-base64-encoded-encryption-key

# ============================================
# FRONTEND
# ============================================
NEXT_PUBLIC_API_URL=https://apextrade.example.com/api
NEXT_PUBLIC_WS_URL=wss://apextrade.example.com/ws
NEXTAUTH_URL=https://apextrade.example.com
NEXTAUTH_SECRET=your-nextauth-secret

# ============================================
# MONITORING
# ============================================
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=secure-password-here
GRAFANA_ROOT_URL=https://apextrade.example.com/grafana

# ============================================
# EMAIL (OPTIONAL)
# ============================================
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=email-password
SMTP_FROM=ApexTrade <noreply@apextrade.example.com>

# ============================================
# BROKER APIS (OPTIONAL - LIVE TRADING)
# ============================================
# Alpaca
ALPACA_API_KEY=
ALPACA_SECRET_KEY=
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Binance
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
BINANCE_TESTNET=true
```

### 4.2 Generate Secure Secrets

```bash
# Generate SECRET_KEY (64 characters)
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY (32 bytes, base64)
openssl rand -base64 32

# Generate passwords
openssl rand -base64 24

# Example script to generate all secrets
#!/bin/bash
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
echo "ENCRYPTION_KEY=$(openssl rand -base64 32)"
echo "POSTGRES_PASSWORD=$(openssl rand -base64 24)"
echo "TIMESCALE_PASSWORD=$(openssl rand -base64 24)"
echo "REDIS_PASSWORD=$(openssl rand -base64 24)"
echo "MINIO_ROOT_PASSWORD=$(openssl rand -base64 24)"
echo "GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 24)"
echo "NEXTAUTH_SECRET=$(openssl rand -base64 32)"
```

---

## 5. Service Configuration

### 5.1 Nginx Configuration

```nginx
# nginx/nginx.conf
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
    use epoll;
    multi_accept on;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout  65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript 
               application/xml application/xml+rss text/javascript;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;

    # Include server configurations
    include /etc/nginx/conf.d/*.conf;
}
```

```nginx
# nginx/conf.d/apextrade.conf
upstream frontend {
    server frontend:3000;
}

upstream api {
    server api:8000;
}

upstream grafana {
    server grafana:3000;
}

upstream flower {
    server celery_flower:5555;
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name apextrade.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name apextrade.example.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/apextrade.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/apextrade.example.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # API endpoints
    location /api/ {
        limit_req zone=api_limit burst=50 nodelay;
        
        proxy_pass http://api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket endpoint
    location /ws/ {
        proxy_pass http://api/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeouts
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # Grafana
    location /grafana/ {
        proxy_pass http://grafana/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Flower (Celery monitoring) - restrict access
    location /flower/ {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://flower/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Frontend (Next.js)
    location / {
        limit_req zone=general burst=20 nodelay;
        
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Next.js HMR (development only)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }

    # Static files cache
    location /_next/static {
        proxy_pass http://frontend;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
}
```

---

## 6. SSL/TLS Configuration

### 6.1 Let's Encrypt with Certbot

```bash
# Create certbot directories
mkdir -p certbot/conf certbot/www

# Initial certificate request
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@example.com \
    --agree-tos \
    --no-eff-email \
    -d apextrade.example.com

# Certbot service for renewal
```

**Add to docker-compose.yml:**

```yaml
services:
  certbot:
    image: certbot/certbot:latest
    container_name: apextrade-certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

### 6.2 Automatic Renewal Cron

```bash
# /etc/cron.d/certbot-renewal
0 0 * * * root docker compose run --rm certbot renew --quiet && docker compose exec nginx nginx -s reload
```

---

## 7. Monitoring Setup

### 7.1 Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  - job_name: 'celery'
    static_configs:
      - targets: ['celery_flower:5555']
```

### 7.2 Grafana Dashboard Provisioning

```yaml
# monitoring/grafana/provisioning/datasources/datasources.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false

  - name: PostgreSQL
    type: postgres
    url: postgres:5432
    database: apextrade
    user: apextrade
    secureJsonData:
      password: ${POSTGRES_PASSWORD}
    jsonData:
      sslmode: disable
      maxOpenConns: 5
      maxIdleConns: 2
```

### 7.3 Alert Rules

```yaml
# monitoring/prometheus/rules/alerts.yml
groups:
  - name: apextrade
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High CPU usage detected

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High memory usage detected

      - alert: APIHighLatency
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: API p95 latency > 1s

      - alert: DatabaseConnectionErrors
        expr: rate(pg_stat_activity_count{state="active"}[5m]) > 100
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High database connection activity

      - alert: CeleryQueueBacklog
        expr: celery_task_queue_length > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: Celery task queue has backlog
```

---

## 8. Backup & Recovery

### 8.1 Backup Script

```bash
#!/bin/bash
# scripts/backup.sh

set -e

BACKUP_DIR="/backups/apextrade"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "${BACKUP_DIR}/${DATE}"

echo "Starting backup: ${DATE}"

# PostgreSQL backup
echo "Backing up PostgreSQL..."
docker compose exec -T postgres pg_dump -U apextrade apextrade | gzip > "${BACKUP_DIR}/${DATE}/postgres.sql.gz"

# TimescaleDB backup
echo "Backing up TimescaleDB..."
docker compose exec -T timescaledb pg_dump -U apextrade_ts apextrade_ts | gzip > "${BACKUP_DIR}/${DATE}/timescale.sql.gz"

# Redis backup (RDB snapshot)
echo "Backing up Redis..."
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} BGSAVE
sleep 5
docker cp apextrade-redis:/data/dump.rdb "${BACKUP_DIR}/${DATE}/redis.rdb"

# MinIO backup (sync to backup location)
echo "Backing up MinIO..."
docker run --rm --network apextrade_apextrade \
    -v "${BACKUP_DIR}/${DATE}:/backup" \
    minio/mc:latest \
    mirror minio/apextrade-data /backup/minio

# Compress entire backup
echo "Compressing backup..."
tar -czf "${BACKUP_DIR}/apextrade_${DATE}.tar.gz" -C "${BACKUP_DIR}" "${DATE}"
rm -rf "${BACKUP_DIR}/${DATE}"

# Cleanup old backups
echo "Cleaning old backups..."
find "${BACKUP_DIR}" -name "apextrade_*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "Backup completed: apextrade_${DATE}.tar.gz"
```

### 8.2 Restore Script

```bash
#!/bin/bash
# scripts/restore.sh

set -e

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file.tar.gz>"
    exit 1
fi

echo "WARNING: This will overwrite existing data!"
read -p "Continue? (y/N): " confirm
if [ "$confirm" != "y" ]; then
    exit 0
fi

RESTORE_DIR="/tmp/apextrade_restore"
mkdir -p "${RESTORE_DIR}"

# Extract backup
echo "Extracting backup..."
tar -xzf "${BACKUP_FILE}" -C "${RESTORE_DIR}"
BACKUP_NAME=$(ls "${RESTORE_DIR}")

# Stop services
echo "Stopping services..."
docker compose stop api celery_worker celery_beat

# Restore PostgreSQL
echo "Restoring PostgreSQL..."
docker compose exec -T postgres psql -U apextrade -d postgres -c "DROP DATABASE IF EXISTS apextrade;"
docker compose exec -T postgres psql -U apextrade -d postgres -c "CREATE DATABASE apextrade;"
gunzip -c "${RESTORE_DIR}/${BACKUP_NAME}/postgres.sql.gz" | docker compose exec -T postgres psql -U apextrade apextrade

# Restore TimescaleDB
echo "Restoring TimescaleDB..."
docker compose exec -T timescaledb psql -U apextrade_ts -d postgres -c "DROP DATABASE IF EXISTS apextrade_ts;"
docker compose exec -T timescaledb psql -U apextrade_ts -d postgres -c "CREATE DATABASE apextrade_ts;"
gunzip -c "${RESTORE_DIR}/${BACKUP_NAME}/timescale.sql.gz" | docker compose exec -T timescaledb psql -U apextrade_ts apextrade_ts

# Restore Redis
echo "Restoring Redis..."
docker compose stop redis
docker cp "${RESTORE_DIR}/${BACKUP_NAME}/redis.rdb" apextrade-redis:/data/dump.rdb
docker compose start redis

# Start services
echo "Starting services..."
docker compose up -d

# Cleanup
rm -rf "${RESTORE_DIR}"

echo "Restore completed!"
```

### 8.3 Automated Backup Cron

```bash
# /etc/cron.d/apextrade-backup
# Daily backup at 3 AM
0 3 * * * root /opt/apextrade/scripts/backup.sh >> /var/log/apextrade-backup.log 2>&1
```

---

## 9. Production Checklist

### 9.1 Pre-Deployment

- [ ] All secrets generated and stored securely
- [ ] `.env` file configured (not committed to git)
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Firewall rules configured
- [ ] Backup storage configured

### 9.2 Security

- [ ] Change all default passwords
- [ ] Enable 2FA for admin accounts
- [ ] Configure rate limiting
- [ ] Set up fail2ban
- [ ] Disable debug mode
- [ ] Configure CORS properly
- [ ] Review security headers

### 9.3 Performance

- [ ] Configure connection pooling
- [ ] Set up Redis caching
- [ ] Enable gzip compression
- [ ] Configure CDN (optional)
- [ ] Tune PostgreSQL settings
- [ ] Set resource limits in Docker

### 9.4 Monitoring

- [ ] Prometheus scraping all services
- [ ] Grafana dashboards configured
- [ ] Alert rules configured
- [ ] Log aggregation working
- [ ] Uptime monitoring configured

### 9.5 Disaster Recovery

- [ ] Backup script tested
- [ ] Restore procedure documented
- [ ] Backup retention policy set
- [ ] Off-site backup copy configured

---

## 10. Troubleshooting

### 10.1 Common Issues

**Container won't start:**
```bash
# Check logs
docker compose logs <service_name>

# Check health
docker compose ps

# Inspect container
docker inspect apextrade-<service>
```

**Database connection errors:**
```bash
# Check PostgreSQL logs
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U apextrade -d apextrade -c "SELECT 1"

# Check connections
docker compose exec postgres psql -U apextrade -d apextrade -c "SELECT count(*) FROM pg_stat_activity"
```

**Redis issues:**
```bash
# Check Redis
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} ping

# Check memory
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} info memory
```

**Celery tasks not processing:**
```bash
# Check worker status
docker compose logs celery_worker

# Check queue
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} llen celery

# Restart workers
docker compose restart celery_worker
```

### 10.2 Performance Debugging

```bash
# API response times
docker compose exec api curl -o /dev/null -s -w "%{time_total}\n" http://localhost:8000/health

# Database slow queries
docker compose exec postgres psql -U apextrade -d apextrade -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Container resource usage
docker stats --no-stream
```

### 10.3 Logs Access

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100 api

# With timestamps
docker compose logs -t api
```

---

## Deployment Commands Reference

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Rebuild and start
docker compose up -d --build

# View logs
docker compose logs -f

# Scale workers
docker compose up -d --scale celery_worker=3

# Run database migrations
docker compose exec api alembic upgrade head

# Enter container shell
docker compose exec api /bin/bash

# Prune unused images
docker system prune -a
```

---

*Document End*
