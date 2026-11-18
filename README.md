# Creator-API

[![CI/CD Pipeline & Docker Image Build](https://github.com/om0852/Creator-API/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/om0852/Creator-API/actions/workflows/ci-cd.yml)
[![Docker Image](https://img.shields.io/badge/docker%20image-ghcr.io%2Fom0852%2Fcreator--api-blue?logo=docker)](https://github.com/om0852/Creator-API/pkgs/container/creator-api)

A high-performance FastAPI microservice for creator & influencer discovery with deep filtering, rate-limit defense, caching, and auto-pagination.

---

## 🐳 Docker Image on GitHub Container Registry (GHCR)

The CI/CD pipeline automatically builds and publishes a multi-platform Docker container on every push to `main`:

```bash
docker pull ghcr.io/om0852/creator-api:latest
```

### Run Locally with Docker:
```bash
docker run -p 8000:8000 \
  -e INFLUENCERS_TOKEN="692aac1c64331ae91ffcb8b73a664d999fe05b53" \
  ghcr.io/om0852/creator-api:latest
```

---

## 🚀 Free Cloud Deployment (100% Free, Zero Cost)

### Option 1: Render.com (1-Click Blueprint)
1. Sign in to [render.com](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect `om0852/Creator-API`.
4. Render detects `render.yaml` automatically.
5. Add Environment Variable:
   - `INFLUENCERS_TOKEN` = `692aac1c64331ae91ffcb8b73a664d999fe05b53`
6. Click **Deploy**. Live URL: `https://your-service.onrender.com`.

---

### Option 2: Koyeb (No Sleep / 24/7 Free)
1. Sign in to [koyeb.com](https://www.koyeb.com).
2. Click **Create App** -> **GitHub** -> select `om0852/Creator-API`.
3. Koyeb builds from `Dockerfile` or pulls directly from `ghcr.io/om0852/creator-api:latest`.
4. Add Environment Variable `INFLUENCERS_TOKEN`.
5. Deploy. Live URL: `https://your-app.koyeb.app`.

---

## 🛠️ API Endpoints

- **Interactive Docs**: `GET /docs` (Swagger UI)
- **Health Check**: `GET /health`
- **Search (GET)**: `GET /api/creators/search?query=gaming&location=Delhi,%20India&page=1`
- **Search (POST)**: `POST /api/creators/search`

```json
{
  "keyword": "gaming",
  "location": "Delhi, India",
  "platform": "instagram",
  "page": 1,
  "min_followers": 50000,
  "is_verified": true,
  "has_done_brand_deals": true,
  "has_email": true
}
```

---

## 💻 Local Development

```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
