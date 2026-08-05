# CineOps-AI 🎬🤖

CineOps-AI is an advanced, AI-driven cinematic operations and automation system. It orchestrates complex workflows for generating intelligent media recommendations, engaging social media captions, and relevant hashtags using state-of-the-art AI. Designed for high performance and extensibility, CineOps-AI bridges the gap between raw media data and actionable, AI-enhanced insights.

## Architecture

The project strictly follows **Clean Architecture** principles to ensure separation of concerns, testability, and maintainability:
- **Domain Layer**: Contains core business entities (`MediaItem`, `Recommendation`, `User`) and abstract interfaces.
- **Application Layer**: Orchestrates business use-cases (`WorkflowCoordinator`, `RecommendationService`, `AuthService`).
- **Infrastructure Layer**: Implements external concerns (TMDb/Jikan integrations, Gemini AI, Telegram bots, PostgreSQL DB, Redis caching).
- **Presentation Layer**: Exposes functionality via a FastAPI REST interface and scheduled background jobs.

## Features

- **Intelligent Recommendations**: AI-powered media recommendations based on trending data.
- **Content Generation**: Automatically generates contextual social media captions and hashtags.
- **Workflow Orchestration**: Automated end-to-end pipelines (fetch trends -> filter -> rank -> AI process -> export).
- **Robust Security**: Dual authentication leveraging both static API keys (system-to-system) and JWT (user sessions).
- **High Performance Caching**: Redis-backed caching for AI responses to minimize latency and API costs.
- **Resilience**: Circuit breakers and retry mechanisms for all external providers.
- **Telegram Integration**: Real-time notifications and alerts sent directly to a Telegram channel.

## Technologies Used

- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy 2.x and Alembic
- **Caching**: Redis (asyncio)
- **AI/LLM**: Google Gemini (gemini-3.5-flash-lite)
- **Security**: PyJWT, Passlib (bcrypt)
- **Quality**: Ruff, Black, Mypy, Pytest
- **Containerization**: Docker & Docker Compose

## Installation

Ensure you have Python 3.12 and [uv](https://github.com/astral-sh/uv) installed on your system.

```bash
# Clone the repository
git clone https://github.com/Kevin-JT/CineOps-Ai.git
cd CineOps-Ai

# Create a virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv sync --all-extras --dev
```

## Environment Variables

Copy the provided example environment file and fill in your secrets.

```bash
cp .env.example .env
```

Ensure the following critical variables are set in your `.env` file:
- `TMDB_API_KEY`: Your TMDB API key.
- `GEMINI_API_KEY`: Your Google Gemini API key.
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
- `TELEGRAM_CHAT_ID`: The ID of the Telegram chat to send notifications to.
- `API_KEY_SECRET`: Static API key for protecting system-level endpoints.
- `DATABASE_URL`: Connection string for PostgreSQL.
- `REDIS_URL`: Connection string for Redis.
- `JWT_SECRET_KEY`: Secret key used for signing JWT tokens.

## Running Locally

To start the FastAPI server locally:

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

## Docker Usage

CineOps-AI is fully containerized and includes a `docker-compose.yml` for seamless deployment with PostgreSQL and Redis.

1. Ensure your `.env` file is configured correctly.
2. Build and start the containers:
```bash
docker-compose up -d --build
```
3. The API will be accessible at `http://localhost:8000`. 
4. To view logs:
```bash
docker-compose logs -f app
```
5. To shut down:
```bash
docker-compose down
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user.
- `POST /api/v1/auth/login` - Authenticate and receive JWT tokens.
- `POST /api/v1/auth/refresh` - Refresh an expired access token.

### Recommendations (Requires JWT / API Key)
- `POST /api/v1/recommendations/generate` - Generate AI recommendations (API Key).
- `GET /api/v1/recommendations` - List recommendation history (JWT).
- `GET /api/v1/recommendations/{id}` - Get a specific recommendation (JWT).
- `DELETE /api/v1/recommendations/{id}` - Delete a recommendation (JWT).

### Workflows (Requires API Key)
- `POST /api/v1/workflow/run` - Trigger the end-to-end automated workflow pipeline.

### Health & Metrics (Public)
- `GET /api/v1/health` - Check system and dependency health.
- `GET /metrics` - Prometheus metrics endpoint.

*(Note: API Key endpoints expect the `X-API-Key` header, while JWT endpoints expect the `Authorization: Bearer <token>` header).*

## Telegram Integration

The system uses Telegram to dispatch notifications upon the completion of automated workflows. To configure:
1. Create a bot via [BotFather](https://t.me/botfather) and get the token (`TELEGRAM_BOT_TOKEN`).
2. Add the bot to a channel or chat and extract the Chat ID (`TELEGRAM_CHAT_ID`).
3. Ensure these values are present in your `.env`.

## Running Tests

The project maintains high code coverage using `pytest`.

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src
```

## Project Structure

```
CineOps-Ai/
├── src/
│   ├── application/     # Application services (Use Cases)
│   ├── config/          # Configuration and settings
│   ├── core/            # Core utilities, DI container, Exceptions
│   ├── domain/          # Entities, Interfaces, Domain Services
│   ├── infrastructure/  # API Clients, DB Repositories, Caching
│   ├── presentation/    # REST API endpoints, DTOs, Scheduler
│   └── main.py          # FastAPI application entry point
├── tests/               # Pytest suite
├── migrations/          # Alembic database migrations
├── docker-compose.yml   # Docker compose configuration
├── Dockerfile           # Application container image definition
└── pyproject.toml       # Python dependencies and project metadata
```

## Future Improvements

- Implement a sophisticated frontend dashboard.
- Migrate JSON-backed History and Blacklist Repositories to PostgreSQL.
- Add support for multiple LLM providers (e.g., OpenAI, Anthropic) as fallbacks.
- Integrate message queues (e.g., Celery/RabbitMQ) for highly scalable async background processing.
