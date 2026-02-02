# PronIELTS Content Automation - Architecture Document

## 1. Overview

### 1.1 Purpose

This automation pipeline extracts, transcribes, and transforms audio content from multiple sources (YouTube, podcasts, Spotify) into structured English learning materials for the PronIELTS platform. The system generates CEFR-classified phrases, categorized by theme and accent, creating dialogues suitable for pronunciation practice.

### 1.2 Key Objectives

- **Multi-source ingestion**: Support YouTube, RSS feeds, Spotify, and other podcast platforms
- **Automatic transcription**: Convert audio to text with precise timestamps
- **CEFR classification**: Classify phrases by proficiency level (A1-C2)
- **Copyright compliance**: Paraphrase original content to avoid legal issues
- **Accent diversity**: Support American, British, Australian, South African, and other English accents
- **Dialogue generation**: Create short, contextual dialogues (max 10 phrases)
- **Seamless integration**: Feed content directly into PronIELTS platform

### 1.3 Design Principles

| Principle | Description |
|-----------|-------------|
| **Cost-effective** | Use open-source tools (Whisper, Ollama) to minimize operational costs |
| **Scalable** | Kubernetes-based architecture allows horizontal scaling when needed |
| **Modular** | Each component can be updated/replaced independently |
| **Observable** | Built-in logging and monitoring for troubleshooting |
| **Idempotent** | Pipeline can be re-run safely without duplicating data |

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CONTENT SOURCES                                    │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────────┤
│   YouTube   │  Spotify    │  RSS Feeds  │  Apple      │  Other Podcast          │
│   Channels  │  Podcasts   │  (Podcasts) │  Podcasts   │  Platforms              │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴───────────┬─────────────┘
       │             │             │             │                  │
       └─────────────┴─────────────┴─────────────┴──────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         AIRFLOW ORCHESTRATION LAYER                             │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        Airflow Scheduler                                 │   │
│  │  • DAG per source/channel                                                │   │
│  │  • Configurable scheduling (cron)                                        │   │
│  │  • Retry logic and alerting                                              │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      KUBERNETES PROCESSING CLUSTER                              │
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   DOWNLOAD      │  │   TRANSCRIBE    │  │   ANALYZE &     │                  │
│  │   CONTAINER     │  │   CONTAINER     │  │   CLASSIFY      │                  │
│  │                 │  │                 │  │   CONTAINER     │                  │
│  │  • yt-dlp       │  │  • Whisper      │  │                 │                  │
│  │  • spotify-dl   │──▶  (medium/large) │──▶  • Ollama       │                  │
│  │  • podcastparser│  │  • GPU support  │  │  • LLaMA/Mistral│                  │
│  │  • ffmpeg       │  │  • Multi-lang   │  │  • CEFR classify│                  │
│  └─────────────────┘  └─────────────────┘  │  • Paraphraser  │                  │
│                                            │  • Categorizer  │                  │
│                                            └────────┬────────┘                  │
│                                                     │                           │
│  ┌──────────────────────────────────────────────────┴────────────────────────┐  │
│  │                      DIALOGUE GENERATOR CONTAINER                         │  │
│  │  • Selects related phrases                                                │  │
│  │  • Creates coherent dialogues (max 10 phrases)                            │  │
│  │  • Validates CEFR consistency                                             │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA STORAGE LAYER                                    │
│                                                                                 │
│  ┌────────────────────┐    ┌────────────────────┐    ┌────────────────────┐     │
│  │   Raw Audio        │    │   Transcriptions   │    │   Processed Data   │     │
│  │   (MinIO/S3)       │    │   (JSON)           │    │   (PostgreSQL)     │     │
│  │                    │    │                    │    │                    │     │
│  │  • Original MP3    │    │  • Timestamped     │    │  • Phrases         │     │
│  │  • Metadata        │    │  • Segments        │    │  • Dialogues       │     │
│  │  • Source info     │    │  • Word-level      │    │  • Categories      │     │
│  └────────────────────┘    └────────────────────┘    └────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         PRONIELTS INTEGRATION                                   │
│                                                                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐     │
│  │                    Bulk Ingestion API                                  │     │
│  │                                                                        │     │
│  │  POST /api/v1/admin/bulk-import                                        │     │
│  │  • Batch insert phrases                                                │     │
│  │  • Create/update dialogues                                             │     │
│  │  • Assign categories                                                   │     │
│  └────────────────────────────────────────────────────────────────────────┘     │
│                                   │                                             │
│                                   ▼                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐     │
│  │                      PronIELTS Backend                                 │     │
│  │                      (FastAPI + PostgreSQL)                            │     │
│  └────────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Details

### 3.1 Content Sources Module

Responsible for downloading audio from various platforms.

| Source | Tool | Accent Config | Notes |
|--------|------|---------------|-------|
| YouTube | yt-dlp | Per channel | Best for interviews, news, podcasts |
| Spotify | spotify-dl / spotdl | Per show | Requires Spotify API credentials |
| RSS Feeds | podcastparser + requests | Per feed | Standard podcast format |
| Apple Podcasts | yt-dlp (some support) | Per show | Limited, may need workarounds |

**Source Configuration Schema:**
```json
{
  "source_id": "bbc-learning-english",
  "source_type": "youtube",
  "url": "https://www.youtube.com/@bbclearningenglish",
  "accent": "british",
  "default_category": "general",
  "schedule": "0 6 * * MON",
  "enabled": true,
  "metadata": {
    "language": "en",
    "country": "GB",
    "description": "BBC Learning English official channel"
  }
}
```

### 3.2 Transcription Module

Uses OpenAI Whisper for speech-to-text conversion.

**Whisper Model Selection:**

| Model | VRAM | Speed | Quality | Recommended Use |
|-------|------|-------|---------|-----------------|
| tiny | ~1GB | Very fast | Low | Testing only |
| base | ~1GB | Fast | Acceptable | Quick processing |
| small | ~2GB | Moderate | Good | Balance speed/quality |
| **medium** | ~5GB | Slow | Very Good | **Default choice** |
| large-v3 | ~10GB | Very slow | Excellent | High-quality needs |

**Transcription Output Format (JSON):**
```json
{
  "source_id": "bbc-learning-english",
  "episode_id": "ep-2024-001",
  "audio_url": "s3://pronielts-raw/bbc/ep-2024-001.mp3",
  "duration_seconds": 1847,
  "accent": "british",
  "transcription": {
    "language": "en",
    "segments": [
      {
        "id": 1,
        "start": 0.0,
        "end": 4.52,
        "text": "Welcome to BBC Learning English.",
        "words": [
          {"word": "Welcome", "start": 0.0, "end": 0.68, "confidence": 0.98},
          {"word": "to", "start": 0.68, "end": 0.82, "confidence": 0.99},
          {"word": "BBC", "start": 0.82, "end": 1.34, "confidence": 0.97},
          {"word": "Learning", "start": 1.34, "end": 1.92, "confidence": 0.96},
          {"word": "English", "start": 1.92, "end": 2.52, "confidence": 0.98}
        ]
      }
    ]
  },
  "processed_at": "2024-01-15T10:30:00Z"
}
```

### 3.3 Analysis & Classification Module

Uses Ollama with local LLM for intelligent processing.

**Ollama Model Options:**

| Model | Size | Quality | Speed | Recommended |
|-------|------|---------|-------|-------------|
| llama3.2:3b | 2GB | Good | Fast | Quick classification |
| **llama3.1:8b** | 5GB | Very Good | Moderate | **Default choice** |
| mistral:7b | 4GB | Very Good | Moderate | Alternative |
| llama3.1:70b | 40GB | Excellent | Slow | High quality needs |

**Classification Tasks:**

1. **CEFR Level Classification**
   - A1: Beginner
   - A2: Elementary
   - B1: Intermediate
   - B2: Upper Intermediate
   - C1: Advanced
   - C2: Proficiency

2. **Category Classification**
   - Professional / Business
   - Travel / Tourism
   - Restaurant / Food
   - General Conversation
   - IELTS Speaking (Parts 1, 2, 3)
   - News / Current Events
   - Technology
   - Health / Medical
   - Education
   - Entertainment

3. **Paraphrasing**
   - Rewrite original phrases
   - Maintain meaning and difficulty level
   - Use contemporary language
   - Remove podcast-specific references

**Classified Phrase Schema:**
```json
{
  "phrase_id": "uuid-here",
  "original_text": "I'd like to book a table for two at seven o'clock.",
  "paraphrased_text": "Could I reserve a table for two people at 7 PM?",
  "source_segment_id": 42,
  "start_time": 125.3,
  "end_time": 128.7,
  "cefr_level": "B1",
  "category": "restaurant",
  "accent": "british",
  "tags": ["reservation", "formal", "polite"],
  "confidence_scores": {
    "cefr": 0.92,
    "category": 0.88,
    "paraphrase_quality": 0.85
  }
}
```

### 3.4 Dialogue Generator Module

Creates coherent dialogues from classified phrases.

**Dialogue Generation Rules:**
- Maximum 10 phrases per dialogue
- Consistent CEFR level (±1 level allowed)
- Consistent category/theme
- Logical conversation flow
- Natural turn-taking patterns

**Dialogue Schema:**
```json
{
  "dialogue_id": "uuid-here",
  "title": "Making a Restaurant Reservation",
  "category": "restaurant",
  "cefr_level": "B1",
  "accent": "british",
  "phrase_count": 6,
  "phrases": [
    {
      "order": 1,
      "speaker": "A",
      "text": "Good evening, I'd like to make a reservation.",
      "phrase_id": "phrase-uuid-1"
    },
    {
      "order": 2,
      "speaker": "B",
      "text": "Certainly. For how many people?",
      "phrase_id": "phrase-uuid-2"
    }
  ],
  "generated_at": "2024-01-15T12:00:00Z",
  "source_episodes": ["ep-2024-001", "ep-2024-003"]
}
```

---

## 4. Technology Stack

### 4.1 Core Technologies

| Component | Technology | Version | License |
|-----------|------------|---------|---------|
| **Orchestration** | Apache Airflow | 2.8+ | Apache 2.0 |
| **Container Runtime** | Docker | 24+ | Apache 2.0 |
| **Container Orchestration** | Kubernetes (EKS) | 1.28+ | Apache 2.0 |
| **Transcription** | OpenAI Whisper | latest | MIT |
| **LLM Runtime** | Ollama | latest | MIT |
| **LLM Model** | LLaMA 3.1 / Mistral | 8B | Llama 3 Community / Apache 2.0 |
| **Audio Processing** | FFmpeg | 6+ | LGPL |
| **Video/Audio Download** | yt-dlp | latest | Unlicense |
| **Database** | PostgreSQL | 15+ | PostgreSQL License |
| **Object Storage** | MinIO / S3 | latest | AGPL / Proprietary |
| **Language** | Python | 3.11+ | PSF |

### 4.2 Python Dependencies

```txt
# Core
apache-airflow[kubernetes]==2.8.0
openai-whisper==20231117
ollama==0.1.6

# Download
yt-dlp==2024.1.0
podcastparser==0.6.10
spotipy==2.23.0

# Audio Processing
pydub==0.25.1
ffmpeg-python==0.2.0

# Data Processing
pandas==2.1.4
pydantic==2.5.3

# Storage & Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
boto3==1.34.0
minio==7.2.3

# HTTP
httpx==0.26.0
requests==2.31.0

# Utilities
python-dotenv==1.0.0
structlog==24.1.0
```

---

## 5. Data Models

### 5.1 Source Configuration

```sql
CREATE TABLE content_sources (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(100) UNIQUE NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- youtube, spotify, rss, etc.
    url TEXT NOT NULL,
    accent VARCHAR(50) NOT NULL, -- american, british, australian, etc.
    default_category VARCHAR(50),
    schedule VARCHAR(50), -- cron expression
    enabled BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5.2 Episodes (Raw Content)

```sql
CREATE TABLE episodes (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES content_sources(id),
    episode_id VARCHAR(200) UNIQUE NOT NULL,
    title TEXT,
    audio_url TEXT,
    duration_seconds INTEGER,
    transcription JSONB, -- full transcription with timestamps
    status VARCHAR(50) DEFAULT 'pending', -- pending, transcribing, transcribed, processed, failed
    error_message TEXT,
    downloaded_at TIMESTAMP,
    transcribed_at TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5.3 Generated Phrases

```sql
CREATE TABLE generated_phrases (
    id SERIAL PRIMARY KEY,
    phrase_id UUID UNIQUE DEFAULT gen_random_uuid(),
    episode_id INTEGER REFERENCES episodes(id),
    original_text TEXT NOT NULL,
    paraphrased_text TEXT NOT NULL,
    start_time DECIMAL(10, 3),
    end_time DECIMAL(10, 3),
    cefr_level VARCHAR(10) NOT NULL, -- A1, A2, B1, B2, C1, C2
    category VARCHAR(50) NOT NULL,
    accent VARCHAR(50) NOT NULL,
    tags TEXT[],
    confidence_scores JSONB,
    exported_to_pronielts BOOLEAN DEFAULT false,
    pronielts_phrase_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_phrases_cefr ON generated_phrases(cefr_level);
CREATE INDEX idx_phrases_category ON generated_phrases(category);
CREATE INDEX idx_phrases_accent ON generated_phrases(accent);
CREATE INDEX idx_phrases_exported ON generated_phrases(exported_to_pronielts);
```

### 5.4 Generated Dialogues

```sql
CREATE TABLE generated_dialogues (
    id SERIAL PRIMARY KEY,
    dialogue_id UUID UNIQUE DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    cefr_level VARCHAR(10) NOT NULL,
    accent VARCHAR(50) NOT NULL,
    phrase_ids UUID[], -- references to generated_phrases
    exported_to_pronielts BOOLEAN DEFAULT false,
    pronielts_dialog_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_dialogues_cefr ON generated_dialogues(cefr_level);
CREATE INDEX idx_dialogues_category ON generated_dialogues(category);
CREATE INDEX idx_dialogues_exported ON generated_dialogues(exported_to_pronielts);
```

---

## 6. API Contracts

### 6.1 PronIELTS Bulk Import API (New Endpoint)

**Endpoint:** `POST /api/v1/admin/bulk-import`

**Request:**
```json
{
  "dialogues": [
    {
      "title": "Making a Restaurant Reservation",
      "category_name": "Restaurant",
      "difficulty_level": "intermediate",
      "description": "Practice making reservations at restaurants",
      "phrases": [
        {
          "reference_text": "Good evening, I'd like to make a reservation.",
          "order": 1,
          "difficulty": "intermediate",
          "phonetic_transcription": "/ɡʊd ˈiːvnɪŋ aɪd laɪk tə meɪk ə ˌrezərˈveɪʃn/"
        },
        {
          "reference_text": "Certainly. For how many people?",
          "order": 2,
          "difficulty": "intermediate",
          "phonetic_transcription": "/ˈsɜːtnli fɔː haʊ ˈmeni ˈpiːpl/"
        }
      ]
    }
  ],
  "source": "automation-pipeline",
  "batch_id": "batch-2024-01-15-001"
}
```

**Response:**
```json
{
  "success": true,
  "imported": {
    "dialogues": 1,
    "phrases": 2
  },
  "dialogue_ids": [123],
  "batch_id": "batch-2024-01-15-001"
}
```

---

## 7. Security Considerations

### 7.1 Data Protection

| Aspect | Implementation |
|--------|----------------|
| **Audio Storage** | Encrypted at rest (MinIO/S3 SSE) |
| **Database** | PostgreSQL with SSL connections |
| **API Communication** | HTTPS only (cert-manager TLS) |
| **Credentials** | Kubernetes Secrets / AWS Secrets Manager |

### 7.2 Access Control

- Airflow: Role-based access (Admin, User, Viewer)
- Kubernetes: RBAC with least-privilege principle
- API: JWT authentication for admin endpoints
- Network: Internal cluster communication only for processing

### 7.3 Copyright Compliance

- All original content is paraphrased before use
- Source attribution stored but not exposed to end users
- Original audio deleted after processing (configurable)
- Audit trail maintained for compliance

---

## 8. Monitoring & Observability

### 8.1 Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `pipeline_episodes_processed` | Total episodes processed | - |
| `pipeline_transcription_duration` | Time to transcribe | > 30 min |
| `pipeline_classification_errors` | Failed classifications | > 10% |
| `pipeline_phrases_generated` | Phrases per episode | < 5 |
| `pipeline_export_failures` | Failed PronIELTS exports | Any |

### 8.2 Logging

- **Format:** Structured JSON (structlog)
- **Levels:** DEBUG, INFO, WARNING, ERROR
- **Retention:** 30 days
- **Storage:** Kubernetes persistent volume or external (Loki)

### 8.3 Alerting

- Airflow task failures → Slack/Email notification
- Processing queue backup → Slack notification
- Export failures → Email to admin

---

## 9. Disaster Recovery

### 9.1 Backup Strategy

| Component | Frequency | Retention | Location |
|-----------|-----------|-----------|----------|
| PostgreSQL | Daily | 30 days | S3/MinIO |
| Source configs | On change | Indefinite | Git |
| Airflow DAGs | On change | Indefinite | Git |

### 9.2 Recovery Procedures

1. **Database Recovery:** Restore from latest PostgreSQL backup
2. **Pipeline State:** Re-run failed Airflow DAGs (idempotent)
3. **Configuration:** Redeploy from Git repository

---

## 10. Cost Analysis

### 10.1 Infrastructure Costs (Local Kubernetes)

| Component | Resource | Estimated Cost |
|-----------|----------|----------------|
| Kubernetes Node (GPU) | 1x NVIDIA GPU, 32GB RAM | Existing hardware |
| Storage | 500GB NVMe | Existing hardware |
| Network | Local | Free |
| **Total** | | **$0/month** (local) |

### 10.2 Variable Costs

| Service | Usage | Cost |
|---------|-------|------|
| Ollama (Local) | Unlimited | $0 |
| Whisper (Local) | Unlimited | $0 |
| yt-dlp | Unlimited | $0 |
| Spotify API | 1000 req/day | $0 (free tier) |
| **Total** | | **$0/month** |

### 10.3 Comparison: Cloud vs Local LLM

| Approach | Cost per 1M tokens | 5 podcasts/week estimate |
|----------|-------------------|-------------------------|
| OpenAI GPT-4 | ~$30 input, ~$60 output | ~$50-100/month |
| Claude 3.5 | ~$3 input, ~$15 output | ~$10-30/month |
| **Ollama (Local)** | $0 | **$0/month** |

---

## 11. Future Enhancements

### Phase 2 (Future)
- [ ] Real-time streaming transcription
- [ ] Speaker diarization (identify different speakers)
- [ ] Automatic phonetic transcription generation
- [ ] A/B testing for dialogue effectiveness

### Phase 3 (Future)
- [ ] User feedback integration for quality improvement
- [ ] Adaptive difficulty based on user performance
- [ ] Multi-language support (Spanish, French, German)
- [ ] Voice cloning for consistent audio examples

---

## 12. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2024-01-15 | Use Ollama over cloud LLMs | Zero cost, privacy, sufficient quality for classification |
| 2024-01-15 | Whisper medium model as default | Best balance of speed/quality for podcast content |
| 2024-01-15 | Bulk API over message queue | Lower complexity for low volume (1-5/week), no additional infrastructure |
| 2024-01-15 | Paraphrase all content | Copyright compliance, allows commercial use |
| 2024-01-15 | KubernetesExecutor for Airflow | Isolated container per task, resource efficiency |
