# CineOps V2 🎬🤖

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg)](https://ai.google.dev/)
[![Code Style: Black & Ruff](https://img.shields.io/badge/code%20style-black%20%26%20ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: Mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**CineOps V2** is an enterprise-grade, autonomous short-form content strategy and daily media intelligence engine. It orchestrates end-to-end cinematic workflows—from trending media discovery and multi-candidate evaluation to YouTube clip timing verification, 30-day adaptive growth planning, and automated Telegram dispatching.

Built with **Clean Architecture** principles and zero-fabrication guarantees, CineOps V2 empowers content creators to identify high-potential viral opportunities backed by data-driven quality scoring and historical performance learning.

---

## 🌟 CineOps V2 Key Features

### 🧠 30-Day Adaptive Growth Strategy Engine
- **70/30 Exploration vs. Exploitation**: Balances proven high-performing categories (70%) with exploratory content testing (30%) to expand account reach without repetitive fatigue.
- **Account Content Profile**: Automatically analyzes historical engagement metrics (views, likes, shares, comments, retention) to derive account strengths with sample-size confidence controls (`Low`, `Medium`, `High`).
- **Quality-Authoritative Selection**: Weighted candidate ranking (80% Opportunity Score + 20% Strategy Fit) guarantees that exceptional content is never overridden by weak strategic matches.

### 🎥 Multi-Candidate Intelligence & Selection
- **Parallel Candidate Evaluation**: Evaluates top trending candidates concurrently using `asyncio.gather` with full failure isolation.
- **Top Alternatives Summary**: Delivers ranked runner-up alternatives in daily notifications alongside the winner.

### ⏱ Verified Clip Intelligence & Timestamp Discovery
- **Public Transcript Matching**: Searches YouTube timing tracks to match video hooks against actual scene dialogue.
- **Strict Zero-Fabrication Rule**: Enforces `timestamp_verified = False` and `UNVERIFIED` status whenever timing evidence is absent. CineOps V2 *never* fabricates timestamps.

### 🎯 4-Dimension Recommendation Quality Engine
- **Normalized 0–100 Scoring**: Evaluates candidates across Content Potential (30%), Short-Form Potential (30%), Source Quality (20%), and Historical Evidence (20%).
- **Anti-Inflation Capping**: Prevents artificial score inflation with explainable Strengths and Limitations breakdowns.

### ⚡ Failure Resilience & Production Hardening
- **Graceful Provider Degradation**: Isolated fallbacks for Gemini, TMDb, Jikan, YouTube Data API, and Telegram.
- **Telegram Message Chunking**: Automatically splits long updates (max 4000 chars) and falls back to plain text if Markdown syntax errors occur.
- **Automated Daily GitHub Action**: Unattended daily execution scheduled at 07:00 IST / 01:30 UTC with Git-backed history commits.

---

## 🏗️ Architecture & Pipeline Overview

CineOps V2 strictly adheres to **Clean Architecture** and manual **Dependency Injection** (`src/core/di.py`):

```text
               GitHub Actions / Daily Trigger
                             │
                             ▼
                   scripts/run_daily.py
                             │
                             ▼
                   WorkflowCoordinator
                             │
 ┌───────────────────────────┼───────────────────────────┐
 │                           │                           │
 ▼                           ▼                           ▼
Trending Fetch          Deduplication             Quality Filtering
(TMDb / Jikan)       (History / Blacklist)       (Min Rating / Popularity)
 │                           │                           │
 └───────────────────────────┼───────────────────────────┘
                             │
                             ▼
              Multi-Candidate Parallel Pool
                             │
 ┌───────────────────────────┼───────────────────────────┐
 │                           │                           │
 ▼                           ▼                           ▼
Gemini Strategy         YouTube Discovery        Clip Intelligence
(Hook / Editing / Text) (Source Trailers / Clips) (Verified Timestamps)
 │                           │                           │
 └───────────────────────────┼───────────────────────────┘
                             │
                             ▼
              Quality & Strategy Fit Evaluation
        (80% Opportunity Score + 20% Strategy Fit)
                             │
                             ▼
                 Deterministic Winner Selection
                             │
 ┌───────────────────────────┼───────────────────────────┐
 │                           │                           │
 ▼                           ▼                           ▼
History Storage           Markdown Export            Telegram Alert
(Atomic JSON write)       (output/recommendation.md) (Formatted Notification)
```

---

## 📲 Example Daily Telegram Output

```text
🎬 CINEOPS CONTENT OPPORTUNITY

SELECTED FROM 5 CANDIDATES

🧠 30-DAY GROWTH STRATEGY
Day 12 / 30 (Exploitation)

🎯 TODAY'S STRATEGY
Focus: Psychological Thriller
Hook Style: Curiosity Question
Platform: Instagram

📊 STRATEGY FIT: 87/100
💡 WHY: Content matches strategic category 'Psychological Thriller' | Video hook aligns with strategic tone

🎥 MOVIE / SERIES / ANIME
Interstellar (movie)

🎯 OPPORTUNITY SCORE: 91/100 (EXCEPTIONAL)

📊 SCORE BREAKDOWN
Content Potential: 89/100
Short-form Potential: 95/100
Source Quality: 90/100
Historical Evidence: 82/100

💪 WHY THIS WON
• Exceptional viral recognition and rating
• Verified high-quality YouTube source available

⚠️ LIMITATIONS
• Higher production editing complexity

🥈 TOP ALTERNATIVES
2. Oppenheimer — 84/100 (STRONG)
3. Severance — 79/100 (STRONG)

🎯 TARGET AUDIENCE
Sci-fi enthusiasts, thriller fans, cinephiles

🪝 HOOK
"What if the only way forward was to leave everything behind?"

📝 ON-SCREEN TEXT
Opening: The decision that changed humanity.
Middle: 55 years lost in seconds.
Ending: Love is the one thing that transcends dimensions.

✂️ EDITING PLAN
Fast-paced cut between docking sequence and wristwatch signal. High visual contrast.

🎥 BEST CLIP
Docking scene monologue: "No, it's necessary."

⏱ CLIP
03:12 → 03:31 (Duration: 19s)

🎯 CLIP SCORE: 92/100
🔎 VERIFICATION: VERIFIED
💡 WHY THIS CLIP: Transcript dialogue directly matches video hook: 'No, it's necessary.'

▶️ SOURCE
https://youtube.com/watch?v=v123

📝 CAPTION
When survival demands impossible choices... 🚀✨

#️⃣ HASHTAGS
#Interstellar #SciFiMovies #CinemaShorts #FilmTok #CineOps

💬 FIRST COMMENT
Which scene in Interstellar gave you the most chills? Let us know below! 👇
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python**: 3.12+
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (recommended for ultra-fast dependency resolution)

```bash
# Clone the repository
git clone https://github.com/Kevin-JT/CineOps-Ai.git
cd CineOps-Ai

# Initialize virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync --all-extras --dev
```

### Environment Configuration

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Set the required API keys and settings:

```env
# Critical API Keys
TMDB_API_KEY=your_tmdb_api_key
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
YOUTUBE_API_KEY=your_youtube_api_key

# Security & Credentials
API_KEY_SECRET=your_system_api_key_secret
JWT_SECRET_KEY=your_jwt_secret_key

# Storage & Strategy Configuration
STORAGE_PATH=data/storage.json
CANDIDATE_COUNT=5
MIN_OPPORTUNITY_SCORE=60
STRATEGY_DURATION_DAYS=30
EXPLOITATION_RATIO=0.70
EXPLORATION_RATIO=0.30
```

---

## 🚀 Execution & Usage

### 1. Daily CLI Execution (Unattended Pipeline)
Run the daily workflow CLI without launching FastAPI:

```bash
uv run python scripts/run_daily.py
```

### 2. Manual Performance Feedback Recording
Record performance data for past recommendations to update account learning:

```bash
uv run python scripts/record_performance.py --rec-id rec_m1 --views 15000 --likes 1200 --shares 300 --comments 85
```

### 3. FastAPI REST Server
Start the local API server:

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 4. Docker Deployment

```bash
# Start background services with Docker Compose
docker-compose up -d --build

# View logs
docker-compose logs -f app
```

---

## 🧪 Quality & Verification Suite

CineOps V2 enforces strict code quality and test coverage across 140+ unit and integration tests:

```bash
# Run full Pytest test suite
uv run pytest

# Run linting with Ruff
uv run ruff check .

# Check formatting with Black
uv run black --check .

# Run static type checking with Mypy
uv run mypy src tests
```

---

## 📁 Repository Structure

```
CineOps-Ai/
├── .github/workflows/   # Daily scheduled workflow (daily.yml) & CI workflow
├── data/               # Persistent JSON storage (storage.json, cache.json)
├── output/             # Exported Markdown recommendation summaries
├── scripts/            # Daily runner (run_daily.py) & CLI performance recorder
├── src/
│   ├── application/    # WorkflowCoordinator, Recommendation & Trending Services
│   ├── config/         # Environment Settings & Configuration
│   ├── core/           # Dependency Injection Container, Circuit Breaker, Logger
│   ├── domain/         # Entities (Candidate, Clip, Strategy, Quality, Performance)
│   │   ├── models/     # Domain data models
│   │   ├── services/   # QualityEngine, StrategyEngine, ClipIntelligenceService
│   │   └── interfaces.py # Abstract Provider & Repository Contracts
│   ├── infrastructure/ # TMDb, Jikan, Gemini, YouTube, Telegram & Repositories
│   ├── presentation/   # FastAPI REST API controllers & Scheduler runner
│   └── main.py         # FastAPI application entry point
├── tests/              # Comprehensive Pytest suite
├── docker-compose.yml  # Container orchestration
└── pyproject.toml      # Project dependencies & tool configurations
```

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
