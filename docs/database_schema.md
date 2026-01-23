# PronIELTS Database Schema

## Overview

The PronIELTS platform uses a relational database (Azure SQL / PostgreSQL) with four main tables representing the core domain entities.

## Entity Relationship Diagram

```
┌─────────────────┐
│     users       │
│─────────────────│
│ id (PK)         │
│ user_id (UK)    │◄──┐
│ email           │   │
│ full_name       │   │
│ is_active       │   │
│ created_at      │   │
│ updated_at      │   │
└─────────────────┘   │
                      │ 1
                      │
                      │ N
┌─────────────────────┴─────┐
│      assessments          │
│───────────────────────────│
│ id (PK)                   │
│ user_id (FK) ─────────────┘
│ phrase_id (FK) ───────┐
│ accuracy_score        │
│ prosody_score         │
│ fluency_score         │
│ completeness_score    │
│ overall_score         │
│ word_level_scores     │
│ recognized_text       │
│ audio_blob_url        │
│ created_at            │
└───────────────────────┘
                        │
                        │ N
                        │
                        │ 1
                        ▼
┌─────────────────────────┐
│       phrases           │
│─────────────────────────│
│ id (PK)                 │
│ dialog_id (FK) ─────────┼──┐
│ reference_text          │  │
│ order                   │  │
│ phonetic_transcription  │  │
│ difficulty              │  │
└─────────────────────────┘  │
                             │ N
                             │
                             │ 1
                             ▼
                    ┌────────────────┐
                    │    dialogs     │
                    │────────────────│
                    │ id (PK)        │
                    │ title          │
                    │ category       │
                    │ description    │
                    │ difficulty_level│
                    │ created_at     │
                    │ updated_at     │
                    └────────────────┘
```

---

## Table Definitions

### 1. users

Stores user information (anonymous or authenticated).

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_email ON users(email);
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | SERIAL | No | Primary key |
| `user_id` | VARCHAR(100) | No | Anonymous user identifier (UUID) |
| `email` | VARCHAR(255) | Yes | Email address (future use) |
| `full_name` | VARCHAR(255) | Yes | User's full name (future use) |
| `is_active` | BOOLEAN | No | Account status |
| `created_at` | TIMESTAMP | No | Account creation timestamp |
| `updated_at` | TIMESTAMP | Yes | Last update timestamp |

**Constraints**:
- `user_id` must be unique
- `email` must be unique when provided

**Indexes**:
- Primary key index on `id`
- Unique index on `user_id`
- Index on `email` for login lookups

**Sample Data**:
```sql
INSERT INTO users (user_id, email, full_name) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'john@example.com', 'John Doe'),
('6ba7b810-9dad-11d1-80b4-00c04fd430c8', 'jane@example.com', 'Jane Smith');
```

---

### 2. dialogs

Represents themed conversation contexts for practice.

```sql
CREATE TABLE dialogs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    difficulty_level VARCHAR(50) DEFAULT 'Intermediate' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dialogs_category ON dialogs(category);
CREATE INDEX idx_dialogs_difficulty ON dialogs(difficulty_level);
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | SERIAL | No | Primary key |
| `title` | VARCHAR(255) | No | Dialog title |
| `category` | VARCHAR(100) | No | Category enum |
| `description` | TEXT | Yes | Detailed description |
| `difficulty_level` | VARCHAR(50) | No | Difficulty enum |
| `created_at` | TIMESTAMP | No | Creation timestamp |
| `updated_at` | TIMESTAMP | Yes | Last update timestamp |

**Category Enum Values**:
- `Professional`: Work-related scenarios
- `Travel`: Airport, hotel, directions
- `General`: Daily conversation
- `Restaurant`: Dining situations
- `IELTS_Part1`: Personal information questions
- `IELTS_Part2`: Long turn (2-minute talk)
- `IELTS_Part3`: Discussion topics

**Difficulty Enum Values**:
- `Beginner`: A1-A2 level
- `Intermediate`: B1-B2 level
- `Advanced`: C1-C2 level

**Indexes**:
- Primary key index on `id`
- Index on `category` for filtering
- Index on `difficulty_level` for filtering

**Sample Data**:
```sql
INSERT INTO dialogs (title, category, description, difficulty_level) VALUES
('Tech Job Interview', 'Professional', 'Common technical interview questions', 'Advanced'),
('Airport Check-in', 'Travel', 'Essential phrases for airport procedures', 'Beginner'),
('IELTS Speaking Part 1', 'IELTS_Part1', 'Introduction and interview questions', 'Intermediate');
```

---

### 3. phrases

Individual sentences/questions within a dialog for practice.

```sql
CREATE TABLE phrases (
    id SERIAL PRIMARY KEY,
    dialog_id INTEGER NOT NULL REFERENCES dialogs(id) ON DELETE CASCADE,
    reference_text TEXT NOT NULL,
    "order" INTEGER DEFAULT 0 NOT NULL,
    phonetic_transcription TEXT,
    difficulty VARCHAR(50) DEFAULT 'Intermediate' NOT NULL
);

CREATE INDEX idx_phrases_dialog_id ON phrases(dialog_id);
CREATE INDEX idx_phrases_difficulty ON phrases(difficulty);
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | SERIAL | No | Primary key |
| `dialog_id` | INTEGER | No | Foreign key to dialogs |
| `reference_text` | TEXT | No | Text to pronounce |
| `order` | INTEGER | No | Display order (1-based) |
| `phonetic_transcription` | TEXT | Yes | IPA transcription |
| `difficulty` | VARCHAR(50) | No | Difficulty level |

**Constraints**:
- `dialog_id` references `dialogs(id)` with CASCADE delete
- `order` must be non-negative

**Indexes**:
- Primary key index on `id`
- Foreign key index on `dialog_id`
- Index on `difficulty`

**Sample Data**:
```sql
INSERT INTO phrases (dialog_id, reference_text, "order", difficulty) VALUES
(1, 'Can you describe your experience with cloud computing platforms like AWS or Azure?', 1, 'Advanced'),
(1, 'How do you approach debugging a complex software issue?', 2, 'Advanced'),
(2, 'I would like to check in for my flight to London.', 1, 'Beginner'),
(2, 'Do I need to pay for extra baggage?', 2, 'Beginner');
```

---

### 4. assessments

Stores pronunciation assessment results for each user-phrase combination.

```sql
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    phrase_id INTEGER NOT NULL REFERENCES phrases(id) ON DELETE CASCADE,

    -- Scores (0-100 or 0-5 for prosody)
    accuracy_score FLOAT,
    prosody_score FLOAT,
    fluency_score FLOAT,
    completeness_score FLOAT,
    overall_score FLOAT,

    -- Detailed results
    word_level_scores JSONB,
    phoneme_level_scores JSONB,
    recognized_text TEXT,

    -- Metadata
    audio_blob_url VARCHAR(500),
    assessment_duration_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_assessments_user_id ON assessments(user_id);
CREATE INDEX idx_assessments_phrase_id ON assessments(phrase_id);
CREATE INDEX idx_assessments_created_at ON assessments(created_at DESC);
CREATE INDEX idx_assessments_overall_score ON assessments(overall_score);
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | SERIAL | No | Primary key |
| `user_id` | INTEGER | No | Foreign key to users |
| `phrase_id` | INTEGER | No | Foreign key to phrases |
| `accuracy_score` | FLOAT | Yes | Phoneme/word accuracy (0-100) |
| `prosody_score` | FLOAT | Yes | Rhythm/intonation (0-5) |
| `fluency_score` | FLOAT | Yes | Speaking pace (0-100) |
| `completeness_score` | FLOAT | Yes | % of reference text (0-100) |
| `overall_score` | FLOAT | Yes | Aggregated score (0-100) |
| `word_level_scores` | JSONB | Yes | Detailed word scores |
| `phoneme_level_scores` | JSONB | Yes | Phoneme-level details |
| `recognized_text` | TEXT | Yes | Speech-to-text result |
| `audio_blob_url` | VARCHAR(500) | Yes | Blob storage URL |
| `assessment_duration_seconds` | FLOAT | Yes | Audio duration |
| `created_at` | TIMESTAMP | No | Assessment timestamp |

**word_level_scores JSON Structure**:
```json
{
  "Can": {
    "accuracy": 95.0,
    "error_type": "None"
  },
  "you": {
    "accuracy": 88.0,
    "error_type": "None"
  },
  "describe": {
    "accuracy": 72.0,
    "error_type": "Mispronunciation"
  }
}
```

**phoneme_level_scores JSON Structure**:
```json
{
  "describe": [
    {
      "phoneme": "d",
      "accuracy": 85.0
    },
    {
      "phoneme": "ɪ",
      "accuracy": 70.0
    }
  ]
}
```

**Constraints**:
- `user_id` references `users(id)` with CASCADE delete
- `phrase_id` references `phrases(id)` with CASCADE delete
- Scores must be within valid ranges (enforced by application)

**Indexes**:
- Primary key index on `id`
- Foreign key index on `user_id` for user history queries
- Foreign key index on `phrase_id` for phrase analytics
- Index on `created_at` (descending) for recent assessments
- Index on `overall_score` for leaderboards

**Sample Data**:
```sql
INSERT INTO assessments (user_id, phrase_id, accuracy_score, prosody_score, fluency_score, completeness_score, overall_score, recognized_text, audio_blob_url) VALUES
(1, 1, 85.5, 4.2, 78.0, 92.0, 84.9, 'Can you describe your experience with cloud computing?', 'https://blob.../audio123.wav'),
(1, 2, 79.0, 3.8, 82.0, 88.0, 80.7, 'How do you approach debugging a complex software issue?', 'https://blob.../audio124.wav');
```

---

## Relationships

### One-to-Many

1. **dialogs → phrases**: One dialog has many phrases
   - Cascade delete: Deleting a dialog deletes all its phrases

2. **users → assessments**: One user has many assessments
   - Cascade delete: Deleting a user deletes all their assessments

3. **phrases → assessments**: One phrase has many assessments (from different users)
   - Cascade delete: Deleting a phrase deletes all assessments of that phrase

---

## Queries

### Common Queries

#### 1. Get all dialogs with phrase count

```sql
SELECT
    d.id,
    d.title,
    d.category,
    d.difficulty_level,
    COUNT(p.id) as phrase_count
FROM dialogs d
LEFT JOIN phrases p ON d.id = p.dialog_id
GROUP BY d.id, d.title, d.category, d.difficulty_level
ORDER BY d.created_at DESC;
```

#### 2. Get dialog with all phrases

```sql
SELECT
    d.*,
    json_agg(
        json_build_object(
            'id', p.id,
            'reference_text', p.reference_text,
            'order', p.order,
            'difficulty', p.difficulty
        ) ORDER BY p.order
    ) as phrases
FROM dialogs d
LEFT JOIN phrases p ON d.id = p.dialog_id
WHERE d.id = $1
GROUP BY d.id;
```

#### 3. Get user's assessment history

```sql
SELECT
    a.id,
    a.overall_score,
    a.created_at,
    p.reference_text,
    d.title as dialog_title,
    d.category
FROM assessments a
JOIN phrases p ON a.phrase_id = p.id
JOIN dialogs d ON p.dialog_id = d.id
WHERE a.user_id = $1
ORDER BY a.created_at DESC
LIMIT 50 OFFSET $2;
```

#### 4. Get user's average scores

```sql
SELECT
    user_id,
    COUNT(*) as total_assessments,
    AVG(overall_score) as avg_overall,
    AVG(accuracy_score) as avg_accuracy,
    AVG(prosody_score) as avg_prosody,
    AVG(fluency_score) as avg_fluency,
    AVG(completeness_score) as avg_completeness,
    MAX(overall_score) as best_score,
    MIN(overall_score) as worst_score
FROM assessments
WHERE user_id = $1
GROUP BY user_id;
```

#### 5. Get popular categories

```sql
SELECT
    d.category,
    COUNT(a.id) as assessment_count
FROM dialogs d
JOIN phrases p ON d.id = p.dialog_id
JOIN assessments a ON p.id = a.phrase_id
GROUP BY d.category
ORDER BY assessment_count DESC;
```

#### 6. Get score distribution

```sql
SELECT
    CASE
        WHEN overall_score < 60 THEN '0-60'
        WHEN overall_score < 75 THEN '60-75'
        WHEN overall_score < 85 THEN '75-85'
        ELSE '85-100'
    END as score_range,
    COUNT(*) as count
FROM assessments
WHERE overall_score IS NOT NULL
GROUP BY score_range
ORDER BY score_range;
```

#### 7. Get user improvement over time

```sql
WITH monthly_scores AS (
    SELECT
        user_id,
        DATE_TRUNC('month', created_at) as month,
        AVG(overall_score) as avg_score
    FROM assessments
    WHERE user_id = $1
    GROUP BY user_id, DATE_TRUNC('month', created_at)
    ORDER BY month
)
SELECT
    month,
    avg_score,
    LAG(avg_score) OVER (ORDER BY month) as previous_month_score,
    avg_score - LAG(avg_score) OVER (ORDER BY month) as improvement
FROM monthly_scores;
```

---

## Migrations (Alembic)

### Initial Migration

```bash
# Generate initial migration
alembic revision --autogenerate -m "initial schema"

# Apply migration
alembic upgrade head
```

### Example Migration: Add Index

```python
# alembic/versions/002_add_assessment_indexes.py
def upgrade():
    op.create_index(
        'idx_assessments_user_phrase',
        'assessments',
        ['user_id', 'phrase_id']
    )

def downgrade():
    op.drop_index('idx_assessments_user_phrase')
```

---

## Data Integrity

### Referential Integrity
- All foreign keys have `ON DELETE CASCADE`
- Ensures no orphaned records

### Data Validation
- Enforced at application level (Pydantic schemas)
- Scores validated in range (0-100 or 0-5)
- Enum values validated before insert

### Constraints

```sql
-- Add check constraints (optional, enforced by app)
ALTER TABLE assessments
ADD CONSTRAINT check_accuracy_score
CHECK (accuracy_score IS NULL OR (accuracy_score >= 0 AND accuracy_score <= 100));

ALTER TABLE assessments
ADD CONSTRAINT check_prosody_score
CHECK (prosody_score IS NULL OR (prosody_score >= 0 AND prosody_score <= 5));
```

---

## Performance Optimization

### Indexes
- All foreign keys indexed
- Commonly queried fields indexed (category, created_at)
- Composite index for user-phrase lookups

### Partitioning (Future)
```sql
-- Partition assessments by created_at for historical data
CREATE TABLE assessments_2026_01 PARTITION OF assessments
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

### Connection Pooling
- SQLAlchemy pool_size: 10
- max_overflow: 20
- pool_pre_ping: True

---

## Backup & Recovery

### Azure SQL Automated Backups
- Full backup: Weekly
- Differential backup: Daily
- Transaction log backup: Every 5-10 minutes
- Retention: 7 days (free tier), configurable

### Manual Backup
```bash
# PostgreSQL backup
pg_dump -h localhost -U pronielts -d pronielts > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U pronielts -d pronielts < backup_20260123.sql
```

---

## Security

### SQL Injection Prevention
- ✅ Use SQLAlchemy ORM (parameterized queries)
- ✅ Never use raw SQL with string interpolation
- ✅ Validate all inputs with Pydantic

### Row-Level Security (Future)
```sql
-- Enable RLS
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own assessments
CREATE POLICY user_assessments_policy ON assessments
FOR SELECT
USING (user_id = current_setting('app.current_user_id')::integer);
```

### Encryption
- At rest: Azure SQL Transparent Data Encryption (TDE)
- In transit: TLS 1.2+ connections
- Application: Audio files encrypted before storage

---

## Monitoring

### Queries to Monitor
```sql
-- Slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT
    schemaname, tablename, indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## Data Seeding

See [infrastructure/scripts/seed_database.sql](../infrastructure/scripts/seed_database.sql) for complete seed data.

**Summary**:
- 5 dialogs (Professional, Travel, Restaurant, IELTS Part 1, General)
- 25 phrases (5 per dialog)
- Sample user accounts (for testing)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-23
**Database Version**: PostgreSQL 15 / Azure SQL Database
