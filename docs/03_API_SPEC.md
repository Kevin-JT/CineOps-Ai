# CineOps AI

# API Specification

Version: 1.0.0

Status: Draft

Author: Kevin J T

---

# Table of Contents

1. Introduction
2. API Design Philosophy
3. API Standards
4. Naming Conventions
5. Internal Services
6. Data Models
7. Request Standards
8. Response Standards
9. Error Standards
10. Validation Standards
11. Retry Policy
12. Logging Requirements
13. Rate Limiting
14. Common Schemas

---

# 1. Introduction

This document defines every internal API contract used by CineOps AI.

Although the project primarily executes as a scheduled application, every module shall expose a clear service contract.

The API specification ensures:

- loose coupling
- predictable behaviour
- maintainability
- future REST API compatibility
- easier testing
- easier dependency injection

Every service must comply with this specification.

---

# 2. API Design Philosophy

Every service must be:

- deterministic
- stateless whenever possible
- idempotent where applicable
- strongly typed
- fully documented
- independently testable

Every service returns structured data.

No service shall print directly to stdout.

No service shall terminate the application.

Exceptions must be propagated using typed exceptions.

---

# 3. API Standards

All internal services shall follow the same contract.

```
Input

↓

Validation

↓

Execution

↓

Result

↓

Validation

↓

Return
```

Every public function must:

- validate input
- validate output
- log execution
- raise typed exceptions

---

# 4. Naming Convention

Service classes

```
MovieDiscoveryService
AnimeDiscoveryService
GeminiRecommendationService
TelegramNotificationService
```

Repositories

```
HistoryRepository
CacheRepository
ConfigRepository
```

DTOs

```
RecommendationDTO
MovieDTO
AnimeDTO
SeriesDTO
```

Models

```
Recommendation
Movie
Anime
Series
```

Exceptions

```
ApiException
ValidationException
ConfigurationException
```

---

# 5. API Versioning

Current Version

```
v1
```

Future versions

```
v2

v3
```

Backward compatibility should be maintained whenever possible.

---

# 6. Service Categories

The application consists of the following service groups.

## Discovery Services

Responsible for

- fetching movies
- fetching series
- fetching anime

Never perform AI analysis.

---

## AI Services

Responsible for

- recommendation generation
- captions
- hashtags
- hooks
- viral reasoning

Never call Telegram.

Never write files.

---

## Repository Services

Responsible for

- history
- cache
- blacklist
- configuration

Repositories never call external APIs.

---

## Notification Services

Responsible for

Telegram

Discord

Slack

Email

Future integrations.

---

## Export Services

Responsible for

JSON

CSV

Markdown

Text

Future PDF exports.

---

# 7. Base Response Model

Every service shall return a structured object.

Example

```json
{
    "success": true,
    "message": "Movies retrieved successfully.",
    "data": {},
    "metadata": {},
    "timestamp": "2026-08-01T08:00:00Z"
}
```

---

# 8. Success Response

Every successful operation returns

```json
{
  "success": true,
  "message": "Operation completed.",
  "data": {}
}
```

---

# 9. Error Response

Every failed operation returns

```json
{
  "success": false,
  "error": {
    "code": "TMDB_TIMEOUT",
    "message": "TMDb request timed out.",
    "retryable": true
  }
}
```

No stack traces shall be exposed outside the service.

---

# 10. Error Codes

## Discovery

```
TMDB_TIMEOUT

TMDB_RATE_LIMIT

TMDB_INVALID_RESPONSE

JIKAN_TIMEOUT

JIKAN_RATE_LIMIT

NETWORK_ERROR
```

---

## AI

```
GEMINI_TIMEOUT

INVALID_JSON

PROMPT_FAILURE

TOKEN_LIMIT

EMPTY_RESPONSE
```

---

## Storage

```
FILE_NOT_FOUND

INVALID_JSON_FILE

CACHE_CORRUPTED

HISTORY_WRITE_FAILED
```

---

## Notification

```
TELEGRAM_TIMEOUT

INVALID_CHAT_ID

INVALID_TOKEN

MESSAGE_REJECTED
```

---

# 11. Validation Rules

Every service validates:

Input

Output

Response schema

Null values

Required fields

Data types

Maximum lengths

Minimum lengths

Unexpected properties

---

# 12. Logging Requirements

Every request logs

```
Request ID

Service

Start Time

End Time

Duration

Status

Errors

Retries
```

Sensitive information must never be logged.

---

# 13. Retry Policy

Retryable

Timeout

Network Error

Rate Limit

503

502

504

Non-Retryable

401

403

404

422

Invalid JSON

Configuration Errors

---

# 14. Exponential Backoff

Attempt 1

1 second

Attempt 2

2 seconds

Attempt 3

4 seconds

Attempt 4

8 seconds

Maximum

5 attempts

---

# 15. Timeout Standards

TMDb

10 seconds

Jikan

10 seconds

Gemini

30 seconds

Telegram

10 seconds

---

# 16. Request Metadata

Every request internally carries

```json
{
  "request_id": "UUID",
  "timestamp": "...",
  "service": "...",
  "version": "v1"
}
```

---

# 17. Data Transfer Objects (DTOs)

MovieDTO

```json
{
  "id": 123,
  "title": "Interstellar",
  "genre": "Science Fiction",
  "rating": 8.7,
  "popularity": 98.1,
  "release_year": 2014
}
```

---

AnimeDTO

```json
{
  "id": 44,
  "title": "Attack on Titan",
  "season": "Final",
  "rating": 9.2
}
```

---

SeriesDTO

```json
{
  "id": 77,
  "title": "Breaking Bad",
  "rating": 9.5
}
```

---

# 18. Recommendation DTO

```json
{
  "title": "",
  "category": "",
  "scene": "",
  "caption": "",
  "hook": "",
  "hashtags": [],
  "posting_time": "",
  "viral_score": 0,
  "confidence": 0
}
```

---

# 19. Configuration Contract

The configuration service must expose

```
get()

set()

reload()

validate()

reset()
```

Configuration values are immutable during execution.

---

# 20. History Contract

History Repository

Functions

```
save()

exists()

delete()

find()

list()

clear()
```

---

# 21. Cache Contract

```
get()

put()

invalidate()

clear()

contains()
```

---

# 22. Notification Contract

Every notification provider implements

```
connect()

send()

disconnect()

validate()

health_check()
```

Future providers must implement the same interface.

---

# 23. Export Contract

Every exporter supports

```
JSON

CSV

Markdown

Text
```

All exporters implement

```
export()

validate()

write()
```

---

# 24. Health Check

Every service provides

```
health()

status()

version()
```

Returns

```json
{
  "service":"TMDb",
  "status":"healthy",
  "version":"v1"
}
```

---

# 25. Acceptance Criteria

Every service shall

✓ Validate input

✓ Validate output

✓ Return structured responses

✓ Raise typed exceptions

✓ Log execution

✓ Support retries

✓ Pass unit tests

✓ Be independently testable

✓ Follow SOLID principles

---


# Discovery Engine API Specification

---

# 26. Overview

The Discovery Engine is responsible for retrieving entertainment metadata from external providers.

The Discovery Engine is the only layer allowed to communicate with third-party data providers.

Business logic is explicitly prohibited inside discovery services.

Discovery services must only retrieve, validate and normalize data.

---

# 27. Discovery Providers

Current Providers

| Provider | Purpose |
|-----------|----------|
| TMDb | Movies & TV Shows |
| Jikan | Anime |
| Local Cache | Offline Fallback |

Future Providers

IMDb

Trakt

AniList

TVMaze

Crunchyroll

Letterboxd

Rotten Tomatoes

---

# 28. Discovery Service Interface

Every provider must implement the following interface.

```python
class DiscoveryProvider:

    def fetch()

    def validate()

    def normalize()

    def health()

    def provider_name()
```

This interface guarantees that every provider behaves identically.

---

# 29. Discovery Workflow

```
Start

↓

Validate API Key

↓

Validate Internet

↓

Call Provider

↓

Receive Response

↓

Validate JSON

↓

Normalize Objects

↓

Remove Invalid Records

↓

Return DTO List
```

---

# 30. TMDb Service

Class

```
TMDbDiscoveryService
```

Responsibilities

Fetch Trending Movies

Fetch Trending TV

Fetch Popular Movies

Fetch Upcoming Movies

Fetch Top Rated Movies

Fetch Genres

Never perform filtering.

Never generate captions.

Never generate recommendations.

---

# 31. Public Methods

```python
fetch_trending_movies()

fetch_trending_series()

fetch_popular_movies()

fetch_upcoming_movies()

fetch_top_rated_movies()

fetch_movie_details(movie_id)

fetch_tv_details(series_id)

health()

provider_name()
```

---

# 32. Input Contract

Trending request

```json
{
    "language":"en-US",
    "page":1
}
```

Movie Details

```json
{
    "movie_id":157336
}
```

---

# 33. Output Contract

Movie DTO

```json
{
    "id":157336,
    "title":"Interstellar",
    "overview":"",
    "genres":[
        "Science Fiction"
    ],
    "rating":8.7,
    "popularity":98.2,
    "release_date":"2014-11-07",
    "poster_url":"",
    "backdrop_url":"",
    "language":"en",
    "adult":false
}
```

---

# 34. Validation Rules

Reject

Null title

Null id

Missing rating

Adult content

Popularity below configured threshold

Duplicate IDs

Invalid language (configurable)

---

# 35. Jikan Discovery Service

Class

```
AnimeDiscoveryService
```

Responsibilities

Fetch Top Anime

Fetch Seasonal Anime

Fetch Airing Anime

Fetch Popular Anime

Normalize results.

---

# 36. Public Methods

```python
fetch_top_anime()

fetch_seasonal_anime()

fetch_airing_anime()

fetch_popular_anime()

fetch_details(anime_id)

health()
```

---

# 37. Anime DTO

```json
{
    "id":16498,
    "title":"Attack on Titan",
    "episodes":87,
    "rating":9.1,
    "members":4000000,
    "status":"Finished Airing",
    "season":"Winter",
    "year":2013,
    "poster_url":""
}
```

---

# 38. Data Normalization

All providers shall normalize to a shared internal model.

Example

TMDb

```
original_title
```

↓

Internal

```
title
```

Jikan

```
score
```

↓

Internal

```
rating
```

No provider-specific fields may leak outside the Discovery Layer.

---

# 39. Common Media Model

Every provider returns

```json
{
    "id":"",
    "title":"",
    "category":"",
    "rating":0,
    "popularity":0,
    "release_year":0,
    "genres":[],
    "language":"",
    "provider":""
}
```

---

# 40. Data Validation Pipeline

```
API Response

↓

Schema Validation

↓

Required Fields

↓

Data Types

↓

Business Rules

↓

Normalization

↓

DTO Creation
```

---

# 41. Cache Integration

Discovery services shall first check cache.

```
Cache

↓

Exists?

↓

Yes

↓

Return Cache

↓

No

↓

Call Provider
```

Cache expiration

Movies

6 Hours

Anime

6 Hours

Series

6 Hours

---

# 42. Rate Limiting

Providers may return

429

Rate Limit

Required Behaviour

Retry using exponential backoff.

Maximum

Five attempts.

Log every retry.

---

# 43. Error Contracts

Possible Errors

TMDB_TIMEOUT

TMDB_RATE_LIMIT

TMDB_INVALID_SCHEMA

JIKAN_TIMEOUT

NETWORK_FAILURE

INVALID_API_KEY

EMPTY_RESPONSE

CACHE_FAILURE

---

# 44. Health Check Contract

Every provider implements

```python
health()
```

Returns

```json
{
    "provider":"TMDb",
    "status":"Healthy",
    "latency_ms":140,
    "last_success":"2026-08-02T10:15:11Z"
}
```

---

# 45. Logging Contract

Every discovery request logs

Provider

Endpoint

Latency

Retries

Cache Hit

Response Size

HTTP Status

Duration

Correlation ID

---

# 46. Metrics

Capture

Average Response Time

Success Rate

Failure Rate

Cache Hit Rate

Retry Count

API Calls

Timeout Count

Daily Requests

---

# 47. AI Engine Service

Class

```
GeminiRecommendationService
```

Purpose

Transform structured entertainment metadata into actionable social-media recommendations.

The AI Service must never call TMDb or Jikan directly.

It only receives normalized DTOs.

---

# 48. Public Methods

```python
generate_recommendations()

validate_response()

score_response()

repair_json()

health()
```

---

# 49. AI Request Contract

Input

```json
{
    "movies":[],
    "series":[],
    "anime":[],
    "history":[],
    "blacklist":[]
}
```

History prevents duplicate recommendations.

Blacklist excludes unwanted titles.

---

# 50. AI Output Contract

The AI must return **strict JSON only**.

```json
{
  "recommendations":[
    {
      "title":"Interstellar",
      "category":"Movie",
      "scene":"Docking Scene",
      "caption":"Perfection under pressure.",
      "hook":"One mistake changes everything.",
      "hashtags":[
        "#Interstellar",
        "#Cinema"
      ],
      "viral_score":96,
      "confidence":98
    }
  ]
}
```

Markdown, explanatory text, or code fences are not permitted in AI responses.

---

# 51. AI Validation Rules

Reject responses if

JSON is invalid

Required fields are missing

Hashtags exceed configured limit

Caption exceeds configured length

Confidence is outside 0–100

Viral score is outside 0–100

Recommendation already exists in history

---

# 52. AI Recovery Strategy

If validation fails

```
Invalid JSON

↓

Attempt Automatic Repair

↓

Still Invalid?

↓

Retry Gemini

↓

Still Invalid?

↓

Return Typed Exception
```

---

# 53. Acceptance Criteria

The Discovery Engine shall

✓ Retrieve entertainment metadata

✓ Normalize provider responses

✓ Validate every object

✓ Never expose provider-specific schemas

✓ Retry transient failures

✓ Use cache whenever possible

✓ Produce standardized DTOs

✓ Pass all unit tests

The AI Engine shall

✓ Accept only normalized DTOs

✓ Return valid JSON

✓ Never produce duplicate recommendations

✓ Generate complete recommendation objects

✓ Pass schema validation

---


# Recommendation Engine & AI Processing Specification

---

# 54. Purpose

The Recommendation Engine is the core business component of CineOps AI.

It transforms normalized entertainment metadata into high-quality content recommendations optimized for social media platforms.

The engine must balance:

- Popularity
- Diversity
- Engagement
- Recency
- Emotional impact
- Visual quality
- User history

The Recommendation Engine is responsible for decision making.

External providers must never make recommendation decisions.

---

# 55. Recommendation Pipeline

```

Trending Sources

↓

Normalization

↓

Validation

↓

Duplicate Removal

↓

Blacklist Filtering

↓

Popularity Filtering

↓

Recommendation Candidate Pool

↓

AI Analysis

↓

Recommendation Validation

↓

Viral Scoring

↓

Publishing Assets

↓

Export

↓

Notification
```

---

# 56. Recommendation Service

Class

```
RecommendationService
```

Responsibilities

Collect normalized media

Merge providers

Remove duplicates

Filter history

Build AI prompt

Validate AI response

Calculate scores

Generate final recommendation package

Store history

Return structured output

---

# 57. Public Methods

```python
generate()

build_candidate_pool()

remove_duplicates()

filter_blacklist()

filter_history()

rank_candidates()

validate_recommendation()

publish()

health()
```

---

# 58. Candidate Pool Rules

The Recommendation Engine shall collect:

- Top Trending Movies
- Trending TV Series
- Top Anime
- Seasonal Anime
- Upcoming Movies

Minimum candidate pool

```
100 Items
```

Target candidate pool

```
300+ Items
```

The AI should never receive fewer than 50 valid candidates unless external APIs are unavailable.

---

# 59. Candidate Ranking

Before sending data to Gemini, each candidate receives a preliminary score.

Formula

```
Base Score

+

Popularity

+

Rating

+

Trend Multiplier

+

Recent Release Bonus

-

Duplicate Penalty

-

Blacklist Penalty
```

Only the highest-ranked candidates proceed to AI analysis.

---

# 60. Duplicate Prevention

The system shall prevent:

Same movie

Same anime

Same TV show

Same franchise

Repeated actor (optional)

Repeated director (optional)

Repeated genre (configurable)

Repeated recommendation within configurable period

Default history window

```
60 Days
```

---

# 61. Blacklist Behaviour

Blacklist entries override all other scoring.

Example

```
Attack on Titan

↓

Never Recommend
```

Example

```
Marvel Cinematic Universe

↓

Ignore Entire Franchise
```

Supports

Titles

Franchises

Studios

Genres

Keywords

---

# 62. AI Prompt Builder

Class

```
PromptBuilder
```

Responsibilities

Convert DTOs into structured prompt

Inject configuration

Inject blacklist

Inject history

Inject recommendation rules

Inject output schema

The prompt must be deterministic.

---

# 63. Prompt Sections

Every AI request contains

System Instructions

Business Rules

Candidate List

History

Blacklist

Output Schema

Validation Rules

Formatting Rules

Example Output

---

# 64. AI Behaviour Rules

Gemini shall

Choose

1 Movie

1 Anime

1 TV Series

Generate

Best Scene

Reason

Hook

Caption

Hashtags

Search Keywords

Thumbnail Text

Posting Time

Audience

Confidence Score

Viral Score

Spoiler Warning

Clip Duration

Gemini shall never explain its reasoning outside the JSON response.

---

# 65. Output Schema

Every recommendation object

```json
{
  "id":"uuid",
  "title":"",
  "category":"",
  "scene":"",
  "scene_duration":"12-18 seconds",
  "hook":"",
  "caption":"",
  "long_caption":"",
  "hashtags":[],
  "youtube_search":"",
  "alternate_searches":[],
  "thumbnail_text":"",
  "target_audience":"",
  "posting_time":"",
  "viral_score":0,
  "confidence":0,
  "reason":"",
  "spoiler_warning":false
}
```

---

# 66. JSON Validation

Every AI response must pass

JSON parsing

Schema validation

Required field validation

Maximum length validation

Duplicate detection

Confidence validation

Viral score validation

Recommendation uniqueness

---

# 67. Automatic JSON Repair

If Gemini returns malformed JSON

```
Receive Response

↓

Parse

↓

Invalid?

↓

Attempt Automatic Repair

↓

Still Invalid?

↓

Retry AI

↓

Still Invalid?

↓

Raise AIResponseException
```

Maximum repair attempts

```
2
```

Maximum retries

```
3
```

---

# 68. Viral Scoring Engine

Class

```
ViralScoreService
```

Purpose

Estimate engagement potential before publication.

---

# 69. Viral Score Factors

| Factor | Weight |
|---------|-------:|
| Popularity | 20% |
| Community Rating | 15% |
| Emotional Impact | 15% |
| Visual Spectacle | 15% |
| Dialogue Strength | 10% |
| Trend Velocity | 10% |
| Recognizability | 10% |
| AI Confidence | 5% |

Final Score

```
0–100
```

---

# 70. Posting Strategy Engine

Class

```
PostingStrategyService
```

Returns

```json
{
    "best_time":"20:00 IST",
    "platform":"Instagram",
    "recommended_length":"15 seconds",
    "audience":"Movie Fans",
    "content_type":"Reel"
}
```

Future versions may personalise this using analytics.

---

# 71. Recommendation Package

Final object

```json
{
    "recommendation":{},
    "strategy":{},
    "metadata":{},
    "diagnostics":{}
}
```

The package is the only object passed to notification and export services.

---

# 72. Quality Gates

A recommendation cannot be published unless

✓ JSON valid

✓ Caption valid

✓ Viral score ≥ configured threshold

✓ Confidence ≥ configured threshold

✓ Title not blacklisted

✓ Not previously recommended

✓ Required fields present

---

# 73. Recommendation States

```
Draft

↓

Validated

↓

Approved

↓

Published

↓

Archived
```

State transitions must be logged.

---

# 74. Observability

Capture metrics

Recommendations Generated

Recommendations Rejected

Average Viral Score

Average Confidence

Validation Failures

Duplicate Rejections

Blacklist Rejections

AI Retry Count

Average Generation Time

These metrics should be exportable for future dashboards.

---

# 75. Acceptance Criteria

The Recommendation Engine is complete when

✓ Candidate pool is built

✓ Duplicate prevention works

✓ Blacklist is respected

✓ AI prompt is deterministic

✓ AI output passes schema validation

✓ Viral score is calculated

✓ Publishing package is generated

✓ Metrics are recorded

✓ All tests pass

---


# Storage, Export, Notification & Platform Services

---

# 76. Purpose

This section defines every internal service responsible for persistence, exports, notifications, monitoring and platform infrastructure.

These services never contain recommendation logic.

Their only responsibility is executing platform operations.

---

# 77. Service Categories

Infrastructure consists of

Storage Services

↓

Export Services

↓

Notification Services

↓

Monitoring Services

↓

Configuration Services

↓

Health Services

---

# 78. Storage Layer

Storage is abstracted using repositories.

Business logic never accesses files directly.

Current Storage

JSON

Future

SQLite

PostgreSQL

Redis

MongoDB

Every storage backend must implement identical contracts.

---

# 79. Repository Interface

Every repository implements

```python
create()

read()

update()

delete()

exists()

find()

list()

count()

clear()

health()
```

Repositories shall never communicate with external APIs.

---

# 80. History Repository

Purpose

Store previously generated recommendations.

Responsibilities

Save recommendation

Retrieve recommendation

Search recommendation

Check duplicates

Archive old records

Export history

Data Model

```json
{
  "id":"uuid",
  "title":"Interstellar",
  "category":"Movie",
  "generated_at":"2026-08-01T08:00:00Z",
  "viral_score":94,
  "published":true
}
```

---

# 81. Cache Repository

Purpose

Reduce external API calls.

Responsibilities

Cache responses

Invalidate cache

Update cache

Read cache

TTL validation

Recommended TTL

Movies

6 Hours

Anime

6 Hours

Series

6 Hours

---

# 82. Blacklist Repository

Supports

Titles

Genres

Actors

Directors

Studios

Keywords

Franchises

Example

```json
[
    {
        "type":"franchise",
        "value":"Marvel Cinematic Universe"
    }
]
```

---

# 83. Configuration Repository

Purpose

Persist configurable settings.

Examples

Minimum Viral Score

Maximum Caption Length

History Duration

Retry Count

Notification Providers

Languages

Enabled Features

---

# 84. Export Layer

Purpose

Convert recommendation packages into shareable formats.

Current Exporters

JSON

Markdown

CSV

TXT

Future

PDF

Excel

Notion

Google Sheets

---

# 85. Export Interface

Every exporter implements

```python
export()

validate()

write()

health()
```

Output location

```
output/

recommendation.json

recommendation.md

recommendation.csv

recommendation.txt
```

---

# 86. Notification Layer

Notification services deliver recommendation packages.

Current Provider

Telegram

Future Providers

Discord

Slack

Microsoft Teams

Email

Webhook

Push Notification

---

# 87. Notification Provider Interface

Every notification provider implements

```python
connect()

disconnect()

send()

validate()

health()

provider_name()
```

The Recommendation Engine shall never know which notification provider is used.

---

# 88. Telegram Provider

Responsibilities

Validate Bot Token

Validate Chat ID

Escape Markdown

Split oversized messages

Retry failures

Log delivery

Return delivery status

---

# 89. Notification Payload

Every provider receives

```json
{
  "recommendation":{},
  "strategy":{},
  "metadata":{}
}
```

Providers must not modify payload contents.

---

# 90. Export Package

Every recommendation export contains

Recommendation

Strategy

Metrics

Metadata

Generation Time

Version

Checksum

Example

```json
{
    "version":"1.0",
    "generated_at":"",
    "recommendation":{},
    "strategy":{},
    "metrics":{}
}
```

---

# 91. Health Monitoring

Every service implements

```python
health()
```

Response

```json
{
    "service":"HistoryRepository",
    "status":"healthy",
    "latency_ms":3
}
```

---

# 92. Health Manager

Class

```
PlatformHealthService
```

Checks

Storage

AI

Discovery

Telegram

Configuration

Cache

Logging

Export

Reports

Healthy

Warning

Critical

---

# 93. Platform Startup

Workflow

```
Load Configuration

↓

Validate Environment

↓

Validate Secrets

↓

Initialize Logger

↓

Initialize Storage

↓

Initialize Cache

↓

Initialize Discovery Providers

↓

Initialize AI Provider

↓

Initialize Exporters

↓

Initialize Notifications

↓

Ready
```

---

# 94. Shutdown Workflow

```
Flush Logs

↓

Flush Cache

↓

Close Connections

↓

Export Metrics

↓

Shutdown
```

No data shall be lost during shutdown.

---

# 95. Feature Flags

Purpose

Enable or disable features without code changes.

Example

```json
{
    "telegram":true,
    "discord":false,
    "dashboard":false,
    "analytics":true
}
```

Feature flags shall be loaded during startup.

---

# 96. Audit Logging

Critical events

Recommendation Generated

Recommendation Published

History Updated

Blacklist Modified

Configuration Changed

Notification Sent

Export Generated

Every audit entry contains

Timestamp

User

Action

Result

Correlation ID

---

# 97. Metrics Collection

Capture

Execution Time

Discovery Time

AI Time

Export Time

Notification Time

Cache Hits

Cache Misses

Retries

Failures

Average Viral Score

Recommendations Generated

Recommendations Rejected

---

# 98. Platform Diagnostics

Diagnostic Report

```json
{
    "application":"CineOps AI",
    "version":"1.0.0",
    "status":"healthy",
    "services":[],
    "metrics":{},
    "generated_at":""
}
```

Diagnostic reports should be exportable for troubleshooting.

---

# 99. Future Database Compatibility

Repositories must never depend on JSON.

Repositories depend only on interfaces.

Current

JSONRepository

Future

SQLiteRepository

PostgresRepository

MongoRepository

RedisRepository

The service layer must work without modification.

---

# 100. Acceptance Criteria

Storage Layer

✓ CRUD operations implemented

✓ Duplicate detection supported

✓ Repository abstraction complete

Export Layer

✓ JSON export

✓ Markdown export

✓ CSV export

✓ TXT export

Notification Layer

✓ Telegram delivery

✓ Retry support

✓ Markdown escaping

✓ Health checks

Platform

✓ Startup validation

✓ Shutdown sequence

✓ Feature flags

✓ Metrics

✓ Audit logs

✓ Diagnostics

✓ Health monitoring

All infrastructure services shall remain independent from business logic.

---


# Platform Governance, Testing, Observability & API Lifecycle

---

# 101. Purpose

This section defines platform governance standards for CineOps AI.

These requirements ensure every component behaves consistently throughout the application's lifecycle.

The requirements in this section are mandatory.

---

# 102. API Lifecycle

Every execution follows the lifecycle below.

```

Application Start

↓

Environment Validation

↓

Configuration Load

↓

Dependency Initialization

↓

Provider Health Check

↓

Discovery

↓

Normalization

↓

Recommendation

↓

Validation

↓

Export

↓

Notification

↓

Metrics

↓

Shutdown

```

No lifecycle stage may be skipped.

---

# 103. Service Registration

Every service must register itself during startup.

Registration contains

Service Name

Version

Dependencies

Capabilities

Health Status

Example

```json
{
    "service":"RecommendationService",
    "version":"1.0.0",
    "dependencies":[
        "GeminiProvider",
        "HistoryRepository"
    ]
}
```

---

# 104. Dependency Rules

Allowed

```
Presentation

↓

Application

↓

Domain

↓

Infrastructure
```

Forbidden

Repository

↓

Presentation

Notification

↓

Discovery

Export

↓

AI

Circular imports are prohibited.

---

# 105. Provider Discovery

Providers shall be discovered automatically.

Supported providers

Discovery

AI

Notification

Export

Storage

Configuration

Health

Every provider must expose metadata.

```json
{
    "name":"Gemini",
    "version":"1.0",
    "type":"AI"
}
```

---

# 106. Validation Pipeline

Every recommendation passes

```
Schema Validation

↓

Business Validation

↓

Duplicate Detection

↓

Blacklist

↓

Length Validation

↓

Publishing Rules

↓

Export Validation

↓

Notification Validation
```

If any stage fails

Recommendation Status

```
Rejected
```

---

# 107. Recommendation Status Model

Possible states

```
Created

Validated

Queued

Published

Archived

Rejected

Failed
```

State changes shall be immutable and logged.

---

# 108. Quality Gates

Every recommendation must satisfy

Caption length

≤100 characters

Hook length

≤60 characters

Hashtags

3–15

Confidence

≥80

Viral Score

≥75

Spoilers

Allowed only if explicitly configured

Duplicate

Must not exist

Blacklist

Must not match

Language

Must match configured language

---

# 109. AI Governance

The AI Provider shall

Never invent movie titles.

Never invent TV series.

Never invent anime.

Never generate unsafe content.

Never recommend adult content.

Never recommend blacklisted content.

Never generate malformed JSON intentionally.

Always follow the configured output schema.

---

# 110. Prompt Governance

Every prompt must contain

System Instructions

Business Rules

Output Schema

Candidate Data

History

Blacklist

Examples

No prompt shall exceed configured token limits.

---

# 111. Response Governance

AI responses must satisfy

Valid JSON

UTF-8 encoding

Required fields

Correct data types

Length limits

Confidence range

Viral score range

No markdown

No code fences

No explanatory text

---

# 112. Recommendation Audit

Every recommendation stores

Recommendation ID

Generated Time

Generation Duration

Prompt Version

AI Provider

AI Model

Configuration Version

Correlation ID

Recommendation Hash

This allows complete traceability.

---

# 113. Observability

Platform metrics

Discovery Duration

AI Duration

Validation Duration

Export Duration

Notification Duration

Total Runtime

Memory Usage

CPU Usage

Cache Hits

Cache Misses

Retry Count

Failures

Warnings

Average Viral Score

Average Confidence

---

# 114. Structured Logging

Every log entry follows

```json
{
    "timestamp":"",
    "level":"INFO",
    "service":"RecommendationService",
    "correlation_id":"",
    "message":"Recommendation generated"
}
```

Logs must be machine readable.

---

# 115. Event Model

Every significant action creates an event.

Examples

RecommendationCreated

RecommendationValidated

RecommendationPublished

RecommendationRejected

NotificationSent

CacheHit

CacheMiss

ProviderFailure

Future event consumers may subscribe.

---

# 116. Exception Hierarchy

Base

```
ApplicationException
```

Children

ConfigurationException

DiscoveryException

ValidationException

RecommendationException

NotificationException

StorageException

ExportException

ProviderException

AIException

Every exception must contain

Message

Error Code

Retryable

Timestamp

Correlation ID

---

# 117. Testing Contracts

Every public service shall have

Unit Tests

Integration Tests

Mock Tests

Edge Case Tests

Failure Tests

Validation Tests

Repositories shall include persistence tests.

Providers shall include API contract tests.

---

# 118. Mocking Standards

External APIs must never be called during unit testing.

Mock

TMDb

Jikan

Gemini

Telegram

Time

UUID generation

Filesystem

Tests shall be deterministic.

---

# 119. Performance Benchmarks

Application Startup

<2 seconds

Discovery

<15 seconds

AI Recommendation

<30 seconds

Export

<3 seconds

Notification

<5 seconds

Total Execution

<60 seconds

---

# 120. Security Standards

Secrets

Environment variables only

Never committed

Never logged

Never exported

Validate

Environment

API keys

Configuration

JSON

Markdown

Input

Output

Escape all Markdown sent to Telegram.

---

# 121. Versioning

Semantic Versioning

```
MAJOR.MINOR.PATCH
```

Examples

```
1.0.0

1.1.0

1.2.4

2.0.0
```

---

# 122. Deprecation Policy

Deprecated services

Remain supported for one major version.

Deprecation warnings

Must be logged.

Migration path

Must be documented.

---

# 123. Configuration Compatibility

Missing configuration

↓

Default values

↓

Validation

↓

Continue

Invalid configuration

↓

Validation Error

↓

Abort Startup

---

# 124. Continuous Integration Requirements

Every Pull Request must

Run Ruff

Run Black

Run Pytest

Generate Coverage

Validate Documentation

Validate JSON Schemas

Validate Type Hints

No merge permitted if checks fail.

---

# 125. Documentation Standards

Every module shall contain

Module Docstring

Public API Documentation

Type Hints

Usage Examples

Exceptions

Dependencies

Every public function shall be documented.

---

# 126. Future API Compatibility

The architecture shall support

REST API

FastAPI

GraphQL

gRPC

WebSockets

Plugin System

Microservices

without changing domain logic.

---

# 127. Future AI Compatibility

Supported providers

Gemini

OpenAI

Claude

Grok

Mistral

Local LLMs

The Recommendation Engine must remain provider-agnostic.

---

# 128. Production Readiness Checklist

Configuration validated

Logging configured

Health checks passing

Providers healthy

Tests passing

Documentation complete

Coverage ≥90%

No TODO comments

No placeholder implementations

No hardcoded secrets

No circular dependencies

No linting violations

No failing CI jobs

---

# 129. Acceptance Criteria

The API Specification is complete when

✓ All services expose documented contracts

✓ Every DTO is defined

✓ Error handling is standardized

✓ Validation rules are documented

✓ Retry policies are defined

✓ Logging is standardized

✓ Repository contracts exist

✓ Notification contracts exist

✓ Export contracts exist

✓ Testing contracts exist

✓ Security requirements are documented

✓ CI/CD requirements are documented

✓ Future extensibility is preserved

---

# 130. End of API Specification

This document is the authoritative contract governing every service, provider, repository and infrastructure component within CineOps AI.

All future implementations shall conform to this specification.

Any deviation must be documented and approved through architectural review.

---

End of Document
