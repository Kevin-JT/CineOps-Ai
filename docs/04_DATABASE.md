# CineOps AI

# Persistence Architecture & Database Specification

Version: 1.0.0

Status: Draft

Author: Kevin J T

---

# Table of Contents

1. Purpose
2. Persistence Philosophy
3. Architectural Principles
4. Persistence Layers
5. Repository Pattern
6. Entity Model
7. Entity Relationships
8. Storage Architecture
9. JSON Storage Design
10. File Organization
11. Common Data Types
12. Validation Rules
13. Acceptance Criteria

---

# Part 1

# 1. Purpose

This document defines the persistence architecture for CineOps AI.

The persistence layer is responsible for storing, retrieving and managing application data while remaining completely independent of business logic.

The architecture is designed to support multiple storage engines without requiring changes to the Application Layer.

Current implementation

- JSON Storage

Future implementations

- SQLite
- PostgreSQL
- Redis
- MongoDB

The persistence layer shall always expose identical repository contracts regardless of storage technology.

---

# 2. Persistence Philosophy

The persistence layer follows four core principles.

## Storage Independence

Business logic must never know where data is stored.

Whether data exists inside JSON files, SQLite or PostgreSQL should make no difference to the Recommendation Engine.

---

## Repository Abstraction

Repositories expose business operations instead of database operations.

Example

Good

```
history_repository.save(recommendation)
```

Bad

```
INSERT INTO history ...
```

SQL must never appear outside repository implementations.

---

## Immutable History

Historical recommendation records are immutable.

A recommendation may be

Created

Archived

Deleted according to retention policy

It must never be modified after publication.

---

## Future Compatibility

Every persistence decision must support migration to enterprise databases without changing domain services.

---

# 3. Architectural Principles

The persistence layer shall follow

Repository Pattern

Dependency Inversion

Single Responsibility Principle

Interface Segregation

Open/Closed Principle

Persistence Ignorance

No business rules shall exist inside repositories.

Repositories only persist data.

---

# 4. Persistence Architecture

```
                Recommendation Service
                         │
                         ▼
              Repository Interfaces
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 JSON Repository   SQLite Repository   PostgreSQL Repository
        │                │                │
        ▼                ▼                ▼
   JSON Files      SQLite Database     PostgreSQL Database
```

The Application Layer communicates only with repository interfaces.

Storage implementations remain interchangeable.

---

# 5. Repository Pattern

Every repository shall implement a common contract.

```python
class Repository:

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

Repositories may expose additional methods specific to their domain.

Example

HistoryRepository

```python
save_recommendation()

find_by_title()

find_recent()

find_duplicates()

archive()

delete_old()
```

---

# 6. Repository Responsibilities

## History Repository

Stores

- Published recommendations
- Recommendation metadata
- Publishing history

---

## Cache Repository

Stores

- Cached TMDb responses
- Cached Jikan responses
- Cached AI responses (optional)

Supports automatic expiration.

---

## Blacklist Repository

Stores

Titles

Genres

Studios

Actors

Keywords

Franchises

Blacklist entries override recommendation scoring.

---

## Configuration Repository

Stores

Application configuration

Feature flags

Threshold values

Retry limits

Language preferences

Platform settings

---

## Metrics Repository

Stores

Execution metrics

Performance metrics

API latency

Recommendation statistics

Cache statistics

Future analytics

---

# 7. Entity Model

Primary entities

```
Recommendation

Movie

Anime

Series

History

Cache

Blacklist

Configuration

Metrics

AuditLog
```

Every entity owns a unique identifier.

UUID Version 4 is recommended.

---

# 8. Entity Relationship Diagram

```text
                    Recommendation
                           │
                           │
          ┌────────────────┴─────────────────┐
          ▼                                  ▼
      History                         RecommendationMetrics
          │
          │
          ▼
      AuditLog


Cache

Configuration

Blacklist

remain independent entities.
```

History references Recommendation.

AuditLog references History.

Metrics reference Recommendation.

Configuration remains global.

---

# 9. Storage Architecture

Current

```
storage/

history.json

cache.json

blacklist.json

config.json

metrics.json

audit.json
```

Future

```
SQLite

↓

PostgreSQL

↓

Distributed Storage
```

Application code shall not change during migration.

---

# 10. JSON Storage Philosophy

Each file represents a logical collection.

Example

history.json

```json
[
  {
    "id":"uuid",
    "title":"Interstellar"
  }
]
```

Avoid deeply nested structures.

Prefer flat documents.

---

# 11. JSON File Specifications

## history.json

Purpose

Published recommendations.

Primary Key

Recommendation ID

Expected Size

Small to Medium

Retention

Configurable

---

## cache.json

Purpose

Temporary API cache.

TTL

6 Hours

Automatically cleaned.

---

## blacklist.json

Purpose

Content exclusion.

Example

```json
[
  {
    "type":"title",
    "value":"Movie Name"
  }
]
```

---

## config.json

Purpose

Persistent configuration.

Contains

Thresholds

Languages

Feature flags

Notification settings

---

## metrics.json

Stores

Execution statistics.

Average runtime

Average viral score

API latency

Retry count

Recommendation count

---

## audit.json

Stores

Every critical system event.

Append-only.

Never overwrite existing records.

---

# 12. Common Data Types

| Type | Description |
|------|-------------|
| UUID | Primary identifiers |
| String | Text values |
| Integer | Counts |
| Float | Ratings |
| Boolean | Flags |
| Array | Collections |
| Object | Structured data |
| ISO-8601 | Date & Time |

Dates shall always use UTC.

Example

```
2026-08-04T09:15:00Z
```

---

# 13. Naming Standards

Identifiers

snake_case

Repository Classes

PascalCase

JSON Keys

snake_case

Configuration Keys

UPPER_SNAKE_CASE

Example

```
recommendation_id

viral_score

generated_at
```

---

# 14. Validation Rules

Every entity shall satisfy

✓ Primary key exists

✓ Required fields exist

✓ Correct data types

✓ No unknown properties

✓ Valid timestamps

✓ UTF-8 encoding

✓ Maximum field lengths

✓ Business constraints

Invalid records shall never be persisted.

---

# 15. Persistence Lifecycle

```
Recommendation Generated

↓

Validate Entity

↓

Serialize

↓

Repository Save

↓

Integrity Check

↓

Write Storage

↓

Verify Write

↓

Return Success
```

Write verification is mandatory.

---

# 16. Data Integrity Rules

Repositories shall guarantee

No duplicate IDs

Valid foreign references

Consistent timestamps

Schema validation

Atomic writes

Recovery after interrupted writes

Corrupted storage must never silently overwrite valid data.

---

# 17. Acceptance Criteria

The persistence architecture is complete when

✓ Repository abstraction exists

✓ Storage independence is maintained

✓ JSON schema is defined

✓ Entity relationships are documented

✓ Validation rules are documented

✓ File organization is standardized

✓ Naming conventions are consistent

✓ Persistence lifecycle is defined

✓ Data integrity rules are enforced

---

# Relational Database Schema

---

# 18. Purpose

This section defines the relational database model used by CineOps AI.

Although Version 1 stores data in JSON files, every repository shall be designed so that migrating to SQLite or PostgreSQL requires no changes to business logic.

The relational schema defined below is the authoritative model.

---

# 19. Database Engines

Current

```
JSON Storage
```

Planned

```
SQLite
```

Production

```
PostgreSQL
```

Future

```
Cloud SQL

Amazon RDS

Supabase

Neon PostgreSQL
```

---

# 20. Entity Relationship Overview

```
Recommendation
      │
      ├────────────┐
      │            │
      ▼            ▼
RecommendationMetrics
      │
      ▼
History
      │
      ▼
AuditLog


Configuration

Cache

Blacklist

remain independent.
```

---

# 21. Recommendation Table

Table

```
recommendations
```

Purpose

Stores every recommendation generated by the AI.

Columns

| Column | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | UUID | No | Primary Key |
| title | TEXT | No | Movie / Anime / Series title |
| category | TEXT | No | Movie / Anime / Series |
| scene | TEXT | No | Recommended scene |
| hook | TEXT | No | Hook text |
| caption | TEXT | No | Instagram caption |
| long_caption | TEXT | Yes | Extended caption |
| thumbnail_text | TEXT | Yes | Thumbnail title |
| target_audience | TEXT | Yes | Audience |
| posting_time | TEXT | Yes | Suggested posting time |
| spoiler_warning | BOOLEAN | No | Spoiler flag |
| viral_score | INTEGER | No | 0–100 |
| confidence | INTEGER | No | 0–100 |
| recommendation_hash | TEXT | No | Duplicate detection |
| created_at | TIMESTAMP | No | UTC timestamp |

Primary Key

```
id
```

Unique

```
recommendation_hash
```

---

# 22. Recommendation Metrics Table

Table

```
recommendation_metrics
```

Purpose

Stores analytical information.

Columns

| Column | Type |
|---------|------|
| id | UUID |
| recommendation_id | UUID |
| popularity | REAL |
| rating | REAL |
| emotional_score | REAL |
| visual_score | REAL |
| trend_score | REAL |
| ai_confidence | REAL |
| generation_time_ms | INTEGER |

Relationship

```
recommendations

1

↓

Many

recommendation_metrics
```

---

# 23. History Table

Table

```
history
```

Purpose

Prevent duplicate recommendations.

Columns

| Column | Type |
|---------|------|
| id | UUID |
| recommendation_id | UUID |
| published | BOOLEAN |
| published_at | TIMESTAMP |
| platform | TEXT |
| notes | TEXT |

History records shall never be modified after publication.

---

# 24. Cache Table

Table

```
cache
```

Purpose

Temporary API responses.

Columns

| Column | Type |
|---------|------|
| id | UUID |
| provider | TEXT |
| cache_key | TEXT |
| payload | JSON |
| expires_at | TIMESTAMP |
| created_at | TIMESTAMP |

Expired cache entries shall be removed automatically.

---

# 25. Configuration Table

Table

```
configuration
```

Purpose

Persistent application configuration.

Columns

| Column | Type |
|---------|------|
| key | TEXT |
| value | TEXT |
| description | TEXT |
| updated_at | TIMESTAMP |

Examples

```
MIN_VIRAL_SCORE

MAX_CAPTION_LENGTH

DEFAULT_LANGUAGE

ENABLE_TELEGRAM
```

---

# 26. Blacklist Table

Table

```
blacklist
```

Purpose

Exclude content.

Columns

| Column | Type |
|---------|------|
| id | UUID |
| type | TEXT |
| value | TEXT |
| reason | TEXT |
| created_at | TIMESTAMP |

Supported Types

```
Title

Genre

Actor

Director

Studio

Keyword

Franchise
```

---

# 27. Audit Log Table

Table

```
audit_log
```

Purpose

Immutable system audit trail.

Columns

| Column | Type |
|---------|------|
| id | UUID |
| event | TEXT |
| service | TEXT |
| correlation_id | TEXT |
| status | TEXT |
| details | JSON |
| created_at | TIMESTAMP |

Audit entries shall never be updated or deleted.

---

# 28. Execution Metrics Table

Table

```
execution_metrics
```

Purpose

Application performance metrics.

Columns

| Column | Type |
|---------|------|
| id | UUID |
| execution_time_ms | INTEGER |
| discovery_time_ms | INTEGER |
| ai_time_ms | INTEGER |
| export_time_ms | INTEGER |
| notification_time_ms | INTEGER |
| cache_hits | INTEGER |
| cache_misses | INTEGER |
| retry_count | INTEGER |
| created_at | TIMESTAMP |

---

# 29. Foreign Key Relationships

```
recommendations.id

↓

history.recommendation_id
```

```
recommendations.id

↓

recommendation_metrics.recommendation_id
```

Audit logs remain independent.

Configuration remains independent.

Cache remains independent.

---

# 30. Indexing Strategy

Indexes

```
recommendations(title)

recommendations(category)

recommendations(created_at)

recommendations(recommendation_hash)

history(published_at)

history(platform)

cache(cache_key)

cache(expires_at)

blacklist(value)

audit_log(created_at)

execution_metrics(created_at)
```

Indexes should minimise lookup latency.

---

# 31. Constraints

Recommendations

```
viral_score

0–100
```

Confidence

```
0–100
```

Caption

Maximum

```
100 Characters
```

Hook

Maximum

```
60 Characters
```

Category

Allowed

```
Movie

Anime

Series
```

---

# 32. Integrity Constraints

Every recommendation

Must have

Title

Category

Caption

Hook

Created Timestamp

Recommendation Hash

History

Cannot reference non-existent recommendation.

Metrics

Cannot reference non-existent recommendation.

---

# 33. Cascade Behaviour

Recommendation

↓

History

```
RESTRICT
```

Recommendation

↓

Metrics

```
CASCADE
```

Audit Log

```
NO ACTION
```

---

# 34. Data Retention

History

```
365 Days
```

Audit

```
Unlimited
```

Cache

```
6 Hours
```

Execution Metrics

```
180 Days
```

Configuration

```
Permanent
```

Blacklist

```
Permanent
```

Retention periods shall be configurable.

---

# 35. SQLite Compatibility

SQLite shall support

Foreign Keys

Transactions

Indexes

Constraints

JSON Columns (stored as TEXT)

No application changes required.

---

# 36. PostgreSQL Compatibility

PostgreSQL shall support

Native UUID

JSONB

GIN Indexes

Partial Indexes

Full Text Search

Generated Columns

Partitioning

No repository changes required.

---

# 37. Acceptance Criteria

The relational schema is complete when

✓ Primary keys are defined

✓ Foreign keys are documented

✓ Constraints are specified

✓ Indexes are documented

✓ Relationships are defined

✓ Data retention rules exist

✓ SQLite compatibility is documented

✓ PostgreSQL compatibility is documented

✓ Repository abstraction remains unchanged

---


# Repository Contracts, Transactions & Query Specification

---

# 38. Purpose

This section defines how the Application Layer communicates with the persistence layer.

Application services shall never communicate directly with databases, JSON files or SQL statements.

All persistence operations must pass through repository interfaces.

---

# 39. Repository Architecture

```
Application Layer

↓

Repository Interface

↓

Repository Implementation

↓

Storage Engine

↓

JSON

SQLite

PostgreSQL
```

Business services only know about interfaces.

---

# 40. Base Repository Interface

Every repository shall implement the following contract.

```python
class BaseRepository(ABC):

    def create(self, entity): ...

    def get(self, entity_id): ...

    def update(self, entity): ...

    def delete(self, entity_id): ...

    def exists(self, entity_id): ...

    def list(self): ...

    def count(self): ...

    def clear(self): ...

    def health(self): ...
```

Implementations may expose additional domain-specific methods.

---

# 41. History Repository

Class

```
HistoryRepository
```

Purpose

Persist published recommendations.

Required Methods

```python
save_recommendation()

find_by_title()

find_by_hash()

find_recent()

find_by_date()

exists_hash()

archive()

delete_expired()
```

The repository is responsible only for persistence.

Duplicate detection logic belongs to the Recommendation Service.

---

# 42. Cache Repository

Class

```
CacheRepository
```

Required Methods

```python
put()

get()

invalidate()

contains()

cleanup()

clear()

count()
```

Every cached object shall contain

Provider

Key

Payload

Creation Time

Expiration Time

Checksum

---

# 43. Configuration Repository

Class

```
ConfigurationRepository
```

Methods

```python
get()

set()

reload()

validate()

list()

reset_defaults()
```

Configuration changes shall be atomic.

---

# 44. Blacklist Repository

Methods

```python
add()

remove()

contains()

find()

list()

clear()
```

Supported lookup types

Title

Genre

Actor

Director

Studio

Keyword

Franchise

---

# 45. Audit Repository

Methods

```python
append()

find()

list()

count()

export()
```

Audit records are append-only.

No update operation is permitted.

---

# 46. Metrics Repository

Methods

```python
record()

find()

aggregate()

daily_summary()

monthly_summary()

export()
```

Metrics shall support future analytics dashboards.

---

# 47. Repository Return Types

Repositories return domain objects.

Never return

SQL rows

Dictionary objects

Provider-specific payloads

Example

Good

```python
Recommendation(...)
```

Bad

```python
{
   "title":"Interstellar"
}
```

---

# 48. Transactions

Transactions guarantee data consistency.

Workflow

```
Start Transaction

↓

Persist Recommendation

↓

Persist Metrics

↓

Persist History

↓

Commit
```

If any operation fails

```
Rollback
```

JSON storage shall emulate transactional behaviour using temporary files and atomic file replacement.

---

# 49. Atomic Writes

For JSON persistence

Workflow

```
Serialize

↓

Write Temporary File

↓

Validate

↓

Rename

↓

Delete Old Version
```

The original file must never be overwritten directly.

---

# 50. Concurrency

Repositories shall support

Single Writer

Multiple Readers

Future implementations may support concurrent writes using database locking.

---

# 51. Query Specification

Supported query operations

Exact Match

Partial Match

Date Range

Category

Provider

Recommendation Status

Recommendation Hash

Platform

Pagination

Sorting

---

# 52. Pagination

Repository list operations shall support

```python
page

page_size

sort_by

sort_order
```

Example

```
Page

1

↓

20 Records
```

---

# 53. Sorting

Supported fields

Title

Created Date

Viral Score

Confidence

Popularity

Publishing Time

Default

```
created_at DESC
```

---

# 54. Filtering

Repositories shall support

Date

Category

Title

Provider

Published Status

Minimum Viral Score

Minimum Confidence

Blacklist Status

Future filters may be added without breaking existing contracts.

---

# 55. Search Behaviour

Search shall support

Exact

Contains

Starts With

Ends With

Case Insensitive

Unicode Safe

---

# 56. Cache Behaviour

Workflow

```
Lookup Cache

↓

Hit?

↓

Return Payload

↓

Miss

↓

Call Provider

↓

Persist Cache

↓

Return Response
```

Cache entries shall expire automatically.

---

# 57. Cache Keys

Recommended format

```
provider:endpoint:parameters
```

Example

```
tmdb:trending_movies:en-US:page1
```

Cache keys must be deterministic.

---

# 58. Query Performance Targets

Single Record Lookup

<10 ms

History Search

<50 ms

Recommendation Search

<50 ms

Configuration Lookup

<5 ms

Cache Lookup

<5 ms

SQLite and PostgreSQL targets assume local storage.

---

# 59. Repository Validation

Before persisting

Validate Schema

Validate Required Fields

Validate Types

Validate Constraints

Generate Checksum

Persist

After persisting

Read Back

Verify Checksum

Return Success

---

# 60. Checksums

Every persisted recommendation shall generate

SHA-256 checksum

Purpose

Detect corruption

Detect unintended modification

Support migration verification

Checksum shall not be used as the primary key.

---

# 61. Migration Readiness

Every repository shall expose

```python
export()

import()

verify()

migrate()
```

Migration between JSON, SQLite and PostgreSQL shall preserve

Identifiers

Relationships

Timestamps

Checksums

Audit history

---

# 62. Repository Health

Every repository implements

```python
health()
```

Example response

```json
{
    "repository":"HistoryRepository",
    "status":"healthy",
    "records":143,
    "storage":"JSON",
    "latency_ms":2
}
```

---

# 63. Error Handling

Repositories shall raise typed exceptions.

Examples

```
EntityNotFoundException

DuplicateEntityException

StorageUnavailableException

ValidationException

MigrationException

IntegrityException
```

Repositories shall never terminate the application.

---

# 64. Acceptance Criteria

Repository Layer

✓ Interface-based

✓ Storage independent

✓ Domain object returns

✓ Atomic writes

✓ Validation before persistence

✓ Transaction support

✓ Query specification documented

✓ Cache strategy documented

✓ Migration ready

✓ Health checks implemented

✓ Typed exceptions used

---


# Database Operations, Security & Disaster Recovery

---

# 65. Purpose

This section defines operational standards for the CineOps AI persistence layer.

The objective is to ensure that data remains

- Consistent
- Recoverable
- Secure
- Auditable
- Maintainable

under all operating conditions.

---

# 66. Database Lifecycle

Every storage engine follows the lifecycle below.

```
Initialize

↓

Validate Schema

↓

Open Connection

↓

Health Check

↓

Read Operations

↓

Write Operations

↓

Integrity Verification

↓

Backup

↓

Shutdown
```

---

# 67. Schema Versioning

Every storage implementation maintains a schema version.

Example

```text
Schema Version

1.0.0
```

Migration history shall be preserved.

Example

```
1.0.0

↓

1.1.0

↓

2.0.0
```

Schema downgrades are not supported.

---

# 68. Migration Framework

Every repository shall support

```python
migrate()

rollback()

verify_schema()

current_version()

pending_migrations()
```

Migration execution order

```
Backup

↓

Validate

↓

Execute Migration

↓

Verify

↓

Commit

↓

Update Version
```

---

# 69. Migration Rules

Every migration shall

Be idempotent

Be reversible whenever practical

Preserve data

Maintain relationships

Log execution

Verify integrity

A failed migration shall restore the previous state automatically.

---

# 70. Backup Strategy

Supported backup types

Full Backup

Incremental Backup

Manual Backup

Automatic Backup

Export Backup

Future cloud backups may be added without changing repository contracts.

---

# 71. Backup Schedule

Configuration

```
History

Daily

Configuration

On Change

Audit Log

Daily

Metrics

Weekly

Blacklist

On Change
```

Backup frequency shall remain configurable.

---

# 72. Backup Structure

```
backups/

history/

config/

audit/

metrics/

blacklist/

YYYY-MM-DD/

backup.json
```

Future implementations may compress backups automatically.

---

# 73. Restore Process

Workflow

```
Select Backup

↓

Validate

↓

Integrity Check

↓

Restore

↓

Verify

↓

Restart Services
```

Restore operations shall never overwrite valid data without confirmation.

---

# 74. Data Integrity Verification

Every persistence operation shall verify

Checksum

Schema

Required Fields

Relationships

Timestamp

UTF-8 Encoding

Unexpected Properties

Verification occurs before and after writing.

---

# 75. Corruption Detection

Indicators

Invalid JSON

Missing Fields

Broken Relationships

Duplicate IDs

Invalid Checksums

Unexpected Schema

When corruption is detected

```
Stop Write

↓

Log Error

↓

Attempt Recovery

↓

Restore Backup

↓

Notify Application
```

---

# 76. Security Principles

Persistence shall follow

Least Privilege

Secure Defaults

No Plaintext Secrets

Immutable Audit Trail

Input Validation

Output Validation

Secrets shall never be stored inside application data files.

---

# 77. Sensitive Data

Sensitive values include

API Keys

Bot Tokens

Authentication Tokens

Future OAuth Credentials

These values shall exist only in

```
.env
```

Never inside

History

Metrics

Audit

Recommendation

Cache

---

# 78. Encryption Strategy

Current

Environment Variables

Future

AES-256

Encrypted SQLite

Encrypted PostgreSQL

Encrypted Cloud Storage

The architecture shall support encryption without repository changes.

---

# 79. Access Control

Future multi-user support

Roles

Administrator

Editor

Viewer

System

Permissions shall be enforced above the repository layer.

Repositories remain permission-agnostic.

---

# 80. Audit Requirements

Every critical database operation generates an audit event.

Examples

Create Recommendation

Archive Recommendation

Delete Cache

Migration

Restore Backup

Configuration Update

Blacklist Update

Audit events are append-only.

---

# 81. Audit Event Schema

```json
{
    "event_id":"uuid",
    "event":"RecommendationCreated",
    "repository":"HistoryRepository",
    "status":"SUCCESS",
    "timestamp":"2026-08-05T09:00:00Z",
    "correlation_id":"uuid"
}
```

---

# 82. Retention Policy

| Data | Default Retention |
|------|-------------------|
| Recommendations | 365 Days |
| History | 365 Days |
| Cache | 6 Hours |
| Metrics | 180 Days |
| Audit | Unlimited |
| Configuration | Permanent |
| Blacklist | Permanent |

Retention periods shall be configurable.

---

# 83. Archiving Policy

Archived records

Remain readable

Remain searchable

Cannot be modified

Can be restored if required

Archive operations must preserve identifiers.

---

# 84. Cleanup Strategy

Automatic cleanup

Expired Cache

Old Metrics

Temporary Files

Orphaned Backups

Manual cleanup

History

Audit

Archived Records

Cleanup shall never remove active recommendations.

---

# 85. Repository Diagnostics

Every repository exposes

```python
diagnostics()
```

Returns

```json
{
    "repository":"CacheRepository",
    "status":"healthy",
    "records":148,
    "expired_records":4,
    "storage":"JSON",
    "integrity":"verified"
}
```

---

# 86. Storage Health Checks

Health checks verify

Schema

Read Access

Write Access

Available Storage

Permissions

Integrity

Checksum Validation

Every startup shall execute health checks.

---

# 87. Monitoring Metrics

Capture

Database Reads

Database Writes

Average Read Time

Average Write Time

Migration Count

Restore Count

Backup Count

Integrity Failures

Checksum Failures

Storage Size

---

# 88. Disaster Recovery Plan

Failure

↓

Detect

↓

Pause Writes

↓

Recover Latest Valid Backup

↓

Verify Integrity

↓

Resume Operations

↓

Generate Audit Event

Recovery shall prioritise data consistency over availability.

---

# 89. Future Scalability

The persistence layer shall support

SQLite

↓

PostgreSQL

↓

Managed Cloud SQL

↓

Read Replicas

↓

Distributed Storage

without modifying application services.

---

# 90. Acceptance Criteria

Database operations are complete when

✓ Backup strategy documented

✓ Restore process documented

✓ Migration strategy documented

✓ Corruption detection implemented

✓ Integrity verification defined

✓ Security principles documented

✓ Audit events standardised

✓ Retention policy defined

✓ Cleanup strategy documented

✓ Diagnostics implemented

✓ Disaster recovery documented

✓ Future scalability preserved

---


# Future Scalability, Analytics & Production Readiness

---

# 91. Purpose

This section defines the long-term evolution of the CineOps AI persistence layer.

Although Version 1 uses JSON storage, the architecture shall support enterprise deployments without redesigning the domain or application layers.

---

# 92. Persistence Roadmap

Version 1

```
JSON Storage
```

↓

Version 2

```
SQLite
```

↓

Version 3

```
PostgreSQL
```

↓

Version 4

```
Managed Cloud Database
```

↓

Version 5

```
Distributed Database Cluster
```

Repository interfaces shall remain unchanged throughout all stages.

---

# 93. Multi-Environment Support

Supported environments

Development

Testing

Staging

Production

Each environment shall maintain independent storage.

Configuration shall determine which persistence engine is active.

---

# 94. Multi-User Readiness

Future versions may support multiple users.

Recommended entities

```
User

Workspace

Team

Membership

Role
```

Recommendations shall optionally belong to a workspace.

Current Version

Single User

Future Version

Multi Tenant

No repository redesign shall be required.

---

# 95. Workspace Model

Future relationship

```
Workspace

↓

Recommendations

↓

History

↓

Metrics
```

Each workspace shall be isolated.

Cross-workspace access is prohibited.

---

# 96. Analytics Storage

Future analytics shall persist

Daily Recommendations

Weekly Recommendations

Monthly Recommendations

Average Viral Score

Average Confidence

Most Recommended Genres

Most Recommended Categories

Most Successful Posting Times

Analytics shall never modify historical recommendation data.

---

# 97. Analytics Schema

Example

```json
{
  "date":"2026-08-10",
  "recommendations":12,
  "average_viral_score":91,
  "average_confidence":95,
  "top_category":"Movie",
  "top_genre":"Science Fiction"
}
```

Analytics data shall be generated from persisted records.

---

# 98. Trend History

Future trend tracking

Movie Popularity

Anime Popularity

Series Popularity

Genre Popularity

Recommendation Frequency

Platform Performance

Historical trend data shall support dashboard visualisation.

---

# 99. Search Optimisation

Future databases should support

Full Text Search

Fuzzy Search

Prefix Search

Phrase Search

Case-Insensitive Search

Unicode Search

SQLite implementation

FTS5 (optional)

PostgreSQL implementation

GIN indexes with Full Text Search.

---

# 100. Reporting Layer

Future reports

Recommendation Report

Execution Report

Performance Report

Platform Report

Analytics Report

Reports shall be generated from repository interfaces rather than direct database queries.

---

# 101. Event Storage

Future event stream

RecommendationCreated

RecommendationValidated

RecommendationPublished

RecommendationRejected

CacheHit

CacheMiss

ProviderFailure

NotificationSent

Events may later be published to message queues without modifying repositories.

---

# 102. Scalability Strategy

Stage 1

JSON

↓

Stage 2

SQLite

↓

Stage 3

PostgreSQL

↓

Stage 4

Read Replicas

↓

Stage 5

Sharding (if ever required)

The application layer shall remain storage-agnostic.

---

# 103. Performance Targets

JSON

Recommendation lookup

<20 ms

SQLite

Recommendation lookup

<10 ms

PostgreSQL

Recommendation lookup

<5 ms

Cache lookup

<5 ms

Configuration lookup

<2 ms

Performance targets shall be monitored continuously.

---

# 104. Data Governance

Every persisted entity shall include

Creation Time

Last Validation Time

Schema Version

Application Version

Checksum

Correlation ID

This metadata improves traceability and simplifies troubleshooting.

---

# 105. Data Quality Rules

Persisted data must satisfy

Required fields present

Valid identifiers

Valid timestamps

Correct schema version

Checksum verified

No duplicate primary keys

No invalid relationships

Repositories shall reject invalid entities before persistence.

---

# 106. Observability

Persistence metrics

Storage Size

Repository Health

Average Query Time

Average Write Time

Cache Effectiveness

Backup Success Rate

Migration Success Rate

Integrity Verification Success Rate

Metrics shall be exportable for dashboards.

---

# 107. Production Readiness Checklist

Persistence layer

✓ Repository abstraction

✓ Storage independence

✓ Validation

✓ Health checks

✓ Logging

✓ Backup

✓ Restore

✓ Migration

✓ Transactions

✓ Atomic writes

✓ Checksums

✓ Diagnostics

✓ Metrics

✓ Audit logging

✓ Retention policy

✓ Cleanup policy

✓ Schema versioning

---

# 108. Migration Readiness Checklist

Migration to SQLite

✓ Repository compatible

✓ Entities compatible

✓ UUID support

✓ Constraints defined

✓ Relationships defined

✓ Validation unchanged

Migration to PostgreSQL

✓ Native UUID support

✓ JSONB compatible

✓ Index strategy defined

✓ Foreign keys documented

✓ Repository contracts unchanged

---

# 109. Repository Compliance Checklist

Every repository shall

✓ Implement the BaseRepository contract

✓ Return domain objects

✓ Validate before writing

✓ Verify after writing

✓ Raise typed exceptions

✓ Support diagnostics

✓ Support health checks

✓ Support export/import

✓ Avoid business logic

✓ Remain storage independent

---

# 110. Architecture Compliance

The persistence layer shall comply with

Clean Architecture

SOLID Principles

Repository Pattern

Dependency Inversion

Single Responsibility Principle

Open/Closed Principle

Persistence Ignorance

No repository may directly depend on another repository implementation.

---

# 111. Future Enhancements

Planned improvements

SQLite WAL Mode

PostgreSQL Read Replicas

Connection Pooling

Redis Cache

Distributed Cache

Cloud Storage

Automatic Compaction

Incremental Backups

Background Cleanup Jobs

Data Compression

No enhancement shall require changes to domain services.

---

# 112. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| JSON corruption | Atomic writes, checksums, backups |
| Duplicate recommendations | History validation, recommendation hash |
| Cache growth | Automatic expiration and cleanup |
| Migration failure | Backups, verification, rollback |
| Invalid configuration | Startup validation |
| Slow queries | Indexing and caching |
| Storage engine migration | Repository abstraction |

---

# 113. Acceptance Criteria

The Persistence Architecture is considered complete when

✓ Repository interfaces are fully defined

✓ Entity relationships are documented

✓ JSON storage structure is documented

✓ Relational schema is documented

✓ Constraints are defined

✓ Query behaviour is documented

✓ Transaction strategy is documented

✓ Migration strategy is documented

✓ Backup strategy is documented

✓ Restore strategy is documented

✓ Security principles are documented

✓ Data governance rules are documented

✓ Analytics storage is planned

✓ Multi-user readiness is documented

✓ Performance targets are documented

✓ Future scalability is documented

✓ Production readiness checklist is complete

---

# 114. Conclusion

The Persistence Architecture described in this document provides a storage-agnostic foundation for CineOps AI.

The application can begin with lightweight JSON persistence while remaining fully prepared for migration to SQLite, PostgreSQL, or managed cloud databases.

Business logic remains isolated from storage implementation, ensuring maintainability, testability, and long-term scalability.

This document shall serve as the authoritative reference for all persistence-related implementation decisions.

---

End of Document
