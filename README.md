# CineOps-AI 🎬🤖

AI-driven cinematic operations and automation system.

## Clean Architecture
- **Domain**: MediaItem, Recommendation, Caption, Hashtag, Trend
- **Application**: Business workflows and use-cases
- **Infrastructure**: TMDb, Jikan, Gemini, Telegram, and Storage

## Quickstart (Local Development)
```bash
uv venv && source .venv/bin/activate
uv sync --all-extras --dev
pytest
```

## Deployment (Docker)
CineOps AI is fully containerized and production-ready.

1. Ensure your `.env` file is populated with required API keys.
2. Build and start the container via Docker Compose:
```bash
docker-compose up -d --build
```
3. The API will be available at `http://localhost:8000`. Storage is persisted in a Docker volume.
