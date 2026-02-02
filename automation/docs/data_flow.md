# PronIELTS Content Automation - Data Flow Document

## 1. Pipeline Overview

This document describes the complete data flow from content source to PronIELTS integration.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE DATA FLOW                                 │
└──────────────────────────────────────────────────────────────────────────────┘

  ┌─────────┐     ┌──────────┐     ┌─────────┐     ┌─────────┐     ┌──────────┐
  │ INGEST  │ ──▶ │TRANSCRIBE│ ──▶ │ SEGMENT │ ──▶ │CLASSIFY │ ──▶ │PARAPHRASE│
  └─────────┘     └──────────┘     └─────────┘     └─────────┘     └──────────┘
       │               │               │               │               │
       ▼               ▼               ▼               ▼               ▼
   [Audio MP3]   [Raw JSON]    [Phrases JSON]  [Tagged JSON]  [Final JSON]
                                                                      │
                                                                      ▼
                               ┌─────────┐     ┌─────────┐     ┌─────────┐
                               │GENERATE │ ──▶ │ VALIDATE│ ──▶ │ EXPORT  │
                               │DIALOGUES│     │         │     │         │
                               └─────────┘     └─────────┘     └─────────┘
                                    │               │               │
                                    ▼               ▼               ▼
                             [Dialogues]    [Validated]     [PronIELTS]
```

---

## 2. Stage Details

### 2.1 Stage 1: Content Ingestion

**Trigger:** Airflow scheduled DAG or manual trigger

**Input:**
- Source configuration (URL, type, accent)
- Episode metadata (if available)

**Process:**
```python
# Pseudocode for ingestion
def ingest_content(source_config):
    if source_config.type == "youtube":
        audio_path = download_youtube_audio(source_config.url)
    elif source_config.type == "spotify":
        audio_path = download_spotify_episode(source_config.url)
    elif source_config.type == "rss":
        audio_path = download_podcast_rss(source_config.url)

    # Store metadata
    episode = Episode(
        source_id=source_config.id,
        episode_id=generate_episode_id(),
        audio_url=upload_to_storage(audio_path),
        accent=source_config.accent,
        status="downloaded"
    )
    return episode
```

**Output:**
```json
{
  "episode_id": "yt-abc123xyz",
  "source_id": "bbc-learning-english",
  "audio_url": "s3://pronielts-raw/bbc/yt-abc123xyz.mp3",
  "accent": "british",
  "duration_seconds": 1847,
  "title": "6 Minute English - AI and Jobs",
  "status": "downloaded",
  "downloaded_at": "2024-01-15T08:00:00Z"
}
```

**Storage Location:** `s3://pronielts-raw/{source_id}/{episode_id}.mp3`

---

### 2.2 Stage 2: Transcription

**Trigger:** Episode status = "downloaded"

**Input:**
- Audio file (MP3)
- Language hint (English)

**Process:**
```python
# Pseudocode for transcription
def transcribe_audio(episode):
    model = whisper.load_model("medium")

    result = model.transcribe(
        episode.audio_path,
        language="en",
        word_timestamps=True,
        verbose=False
    )

    transcription = {
        "language": result["language"],
        "segments": [
            {
                "id": seg["id"],
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
                "words": seg.get("words", [])
            }
            for seg in result["segments"]
        ]
    }

    episode.transcription = transcription
    episode.status = "transcribed"
    return episode
```

**Output:**
```json
{
  "episode_id": "yt-abc123xyz",
  "transcription": {
    "language": "en",
    "segments": [
      {
        "id": 0,
        "start": 0.0,
        "end": 3.84,
        "text": "Hello and welcome to 6 Minute English.",
        "words": [
          {"word": "Hello", "start": 0.0, "end": 0.48, "confidence": 0.99},
          {"word": "and", "start": 0.48, "end": 0.64, "confidence": 0.98},
          {"word": "welcome", "start": 0.64, "end": 1.12, "confidence": 0.99},
          {"word": "to", "start": 1.12, "end": 1.28, "confidence": 0.97},
          {"word": "6", "start": 1.28, "end": 1.52, "confidence": 0.95},
          {"word": "Minute", "start": 1.52, "end": 1.92, "confidence": 0.98},
          {"word": "English", "start": 1.92, "end": 2.48, "confidence": 0.99}
        ]
      },
      {
        "id": 1,
        "start": 3.84,
        "end": 7.20,
        "text": "I'm Neil and this is Sam.",
        "words": [...]
      }
    ]
  },
  "status": "transcribed",
  "transcribed_at": "2024-01-15T08:15:00Z"
}
```

**Storage Location:** `s3://pronielts-transcriptions/{source_id}/{episode_id}.json`

---

### 2.3 Stage 3: Segmentation

**Trigger:** Episode status = "transcribed"

**Input:**
- Transcription with segments

**Process:**
```python
# Pseudocode for segmentation
def segment_into_phrases(episode):
    phrases = []

    for segment in episode.transcription["segments"]:
        # Filter criteria
        text = segment["text"].strip()

        # Skip short utterances
        if len(text.split()) < 3:
            continue

        # Skip non-sentences (fragments, fillers)
        if not is_complete_sentence(text):
            continue

        # Skip segments with low confidence
        avg_confidence = calculate_avg_confidence(segment["words"])
        if avg_confidence < 0.85:
            continue

        phrase = {
            "segment_id": segment["id"],
            "text": text,
            "start": segment["start"],
            "end": segment["end"],
            "word_count": len(text.split()),
            "confidence": avg_confidence
        }
        phrases.append(phrase)

    return phrases
```

**Output:**
```json
{
  "episode_id": "yt-abc123xyz",
  "phrases": [
    {
      "segment_id": 0,
      "text": "Hello and welcome to 6 Minute English.",
      "start": 0.0,
      "end": 3.84,
      "word_count": 7,
      "confidence": 0.98
    },
    {
      "segment_id": 5,
      "text": "Today we're talking about artificial intelligence and jobs.",
      "start": 15.20,
      "end": 19.84,
      "word_count": 8,
      "confidence": 0.96
    }
  ],
  "total_segments": 245,
  "filtered_phrases": 87,
  "status": "segmented"
}
```

---

### 2.4 Stage 4: CEFR Classification

**Trigger:** Segmentation complete

**Input:**
- List of phrases

**Process:**
```python
# Pseudocode for CEFR classification
CLASSIFICATION_PROMPT = """
Classify the following English phrase according to CEFR levels.

Phrase: "{phrase}"

Consider:
- Vocabulary complexity
- Grammar structures
- Sentence length
- Idiomatic expressions

Respond with JSON only:
{
  "cefr_level": "A1|A2|B1|B2|C1|C2",
  "category": "professional|travel|restaurant|general|news|technology|health|education|entertainment",
  "reasoning": "brief explanation"
}
"""

def classify_phrase(phrase, ollama_client):
    response = ollama_client.generate(
        model="llama3.1:8b",
        prompt=CLASSIFICATION_PROMPT.format(phrase=phrase["text"]),
        format="json"
    )

    classification = json.loads(response)
    phrase["cefr_level"] = classification["cefr_level"]
    phrase["category"] = classification["category"]
    phrase["classification_reasoning"] = classification["reasoning"]

    return phrase
```

**Output:**
```json
{
  "segment_id": 5,
  "text": "Today we're talking about artificial intelligence and jobs.",
  "start": 15.20,
  "end": 19.84,
  "cefr_level": "B1",
  "category": "technology",
  "classification_reasoning": "Uses present continuous, compound noun (artificial intelligence), accessible vocabulary suitable for intermediate learners",
  "confidence": 0.96
}
```

**CEFR Classification Criteria:**

| Level | Vocabulary | Grammar | Example |
|-------|------------|---------|---------|
| A1 | Basic, concrete | Simple present, imperatives | "I like coffee." |
| A2 | Everyday, familiar | Past simple, comparatives | "Yesterday I went shopping." |
| B1 | Common abstract | Present perfect, conditionals | "I've been learning English for two years." |
| B2 | Varied, precise | Passive voice, reported speech | "It's been suggested that AI will transform the workplace." |
| C1 | Sophisticated | Complex structures, nuance | "Had I known about the implications, I would have acted differently." |
| C2 | Full range, idiomatic | All structures, subtle meaning | "The ramifications of such a paradigm shift remain to be seen." |

---

### 2.5 Stage 5: Paraphrasing

**Trigger:** Classification complete

**Input:**
- Classified phrase with original text

**Process:**
```python
# Pseudocode for paraphrasing
PARAPHRASE_PROMPT = """
Paraphrase the following English phrase while:
1. Maintaining the same meaning
2. Keeping the same CEFR level ({cefr_level})
3. Using natural, contemporary English
4. Removing any references to the source (podcast names, hosts, etc.)

Original: "{original_text}"
Category: {category}

Respond with JSON only:
{
  "paraphrased_text": "your paraphrased version",
  "changes_made": "brief description of changes"
}
"""

def paraphrase_phrase(phrase, ollama_client):
    response = ollama_client.generate(
        model="llama3.1:8b",
        prompt=PARAPHRASE_PROMPT.format(
            original_text=phrase["text"],
            cefr_level=phrase["cefr_level"],
            category=phrase["category"]
        ),
        format="json"
    )

    result = json.loads(response)
    phrase["original_text"] = phrase["text"]
    phrase["paraphrased_text"] = result["paraphrased_text"]
    phrase["paraphrase_changes"] = result["changes_made"]

    return phrase
```

**Output:**
```json
{
  "segment_id": 5,
  "original_text": "Today we're talking about artificial intelligence and jobs.",
  "paraphrased_text": "Let's discuss how artificial intelligence is affecting employment.",
  "paraphrase_changes": "Changed 'we're talking about' to 'Let's discuss', replaced 'jobs' with 'employment' for variety",
  "start": 15.20,
  "end": 19.84,
  "cefr_level": "B1",
  "category": "technology"
}
```

---

### 2.6 Stage 6: Dialogue Generation

**Trigger:** Sufficient phrases paraphrased (min 50 per category/level)

**Input:**
- Pool of paraphrased phrases grouped by category and CEFR level

**Process:**
```python
# Pseudocode for dialogue generation
DIALOGUE_PROMPT = """
Create a natural dialogue using the following phrases as inspiration.
The dialogue should:
1. Be 6-10 turns long
2. Have two speakers (A and B)
3. Be contextually coherent
4. Fit the category: {category}
5. Match CEFR level: {cefr_level}

Available phrases for inspiration:
{phrases}

Respond with JSON only:
{
  "title": "Dialogue title",
  "turns": [
    {"speaker": "A", "text": "..."},
    {"speaker": "B", "text": "..."}
  ]
}
"""

def generate_dialogue(phrase_pool, category, cefr_level, ollama_client):
    # Select 5-8 random phrases from pool
    selected_phrases = random.sample(phrase_pool, min(8, len(phrase_pool)))

    response = ollama_client.generate(
        model="llama3.1:8b",
        prompt=DIALOGUE_PROMPT.format(
            category=category,
            cefr_level=cefr_level,
            phrases="\n".join([p["paraphrased_text"] for p in selected_phrases])
        ),
        format="json"
    )

    dialogue = json.loads(response)
    dialogue["category"] = category
    dialogue["cefr_level"] = cefr_level
    dialogue["source_phrases"] = [p["phrase_id"] for p in selected_phrases]

    return dialogue
```

**Output:**
```json
{
  "dialogue_id": "dlg-uuid-here",
  "title": "Discussing AI at Work",
  "category": "technology",
  "cefr_level": "B1",
  "turns": [
    {"speaker": "A", "order": 1, "text": "Have you heard about the new AI tools at our company?"},
    {"speaker": "B", "order": 2, "text": "Yes, I've been reading about them. Do you think they'll affect our jobs?"},
    {"speaker": "A", "order": 3, "text": "I believe they'll change how we work, but not replace us completely."},
    {"speaker": "B", "order": 4, "text": "That's a relief. I was worried about automation."},
    {"speaker": "A", "order": 5, "text": "Actually, AI might help us be more productive."},
    {"speaker": "B", "order": 6, "text": "You're right. We should learn to use these tools effectively."}
  ],
  "source_phrases": ["phrase-uuid-1", "phrase-uuid-2", "phrase-uuid-3"],
  "generated_at": "2024-01-15T10:00:00Z"
}
```

---

### 2.7 Stage 7: Validation

**Trigger:** Dialogue generated

**Input:**
- Generated dialogue

**Validation Rules:**
```python
def validate_dialogue(dialogue):
    errors = []

    # Rule 1: Turn count
    if not (6 <= len(dialogue["turns"]) <= 10):
        errors.append("Dialogue must have 6-10 turns")

    # Rule 2: Alternating speakers
    for i, turn in enumerate(dialogue["turns"]):
        expected_speaker = "A" if i % 2 == 0 else "B"
        if turn["speaker"] != expected_speaker:
            errors.append(f"Turn {i+1}: Expected speaker {expected_speaker}")

    # Rule 3: No empty turns
    for turn in dialogue["turns"]:
        if len(turn["text"].strip()) < 5:
            errors.append(f"Turn {turn['order']}: Text too short")

    # Rule 4: CEFR consistency (use LLM to verify)
    cefr_check = verify_cefr_level(dialogue)
    if not cefr_check["consistent"]:
        errors.append(f"CEFR inconsistency: {cefr_check['reason']}")

    # Rule 5: No source references
    forbidden_patterns = ["6 minute", "bbc", "podcast", "episode"]
    full_text = " ".join([t["text"].lower() for t in dialogue["turns"]])
    for pattern in forbidden_patterns:
        if pattern in full_text:
            errors.append(f"Contains forbidden reference: {pattern}")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
```

**Output:**
```json
{
  "dialogue_id": "dlg-uuid-here",
  "validation": {
    "valid": true,
    "errors": [],
    "checked_at": "2024-01-15T10:05:00Z"
  }
}
```

---

### 2.8 Stage 8: Export to PronIELTS

**Trigger:** Validated dialogues ready for export

**Input:**
- Validated dialogues

**Process:**
```python
def export_to_pronielts(dialogues, api_client):
    # Map CEFR to PronIELTS difficulty
    cefr_to_difficulty = {
        "A1": "beginner",
        "A2": "beginner",
        "B1": "intermediate",
        "B2": "intermediate",
        "C1": "advanced",
        "C2": "advanced"
    }

    payload = {
        "dialogues": [],
        "source": "automation-pipeline",
        "batch_id": f"batch-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
    }

    for dialogue in dialogues:
        pronielts_dialogue = {
            "title": dialogue["title"],
            "category_name": dialogue["category"].title(),
            "difficulty_level": cefr_to_difficulty[dialogue["cefr_level"]],
            "description": f"CEFR {dialogue['cefr_level']} - {dialogue['category'].title()} conversation",
            "phrases": [
                {
                    "reference_text": turn["text"],
                    "order": turn["order"],
                    "difficulty": cefr_to_difficulty[dialogue["cefr_level"]]
                }
                for turn in dialogue["turns"]
            ]
        }
        payload["dialogues"].append(pronielts_dialogue)

    response = api_client.post(
        "/api/v1/admin/bulk-import",
        json=payload,
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )

    return response.json()
```

**Output:**
```json
{
  "success": true,
  "imported": {
    "dialogues": 5,
    "phrases": 38
  },
  "dialogue_ids": [101, 102, 103, 104, 105],
  "batch_id": "batch-2024-01-15-100530"
}
```

---

## 3. Data Transformation Summary

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STAGE           │ INPUT FORMAT        │ OUTPUT FORMAT       │ STORAGE           │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. Ingest       │ URL                 │ MP3 + Metadata      │ S3: /raw/         │
│ 2. Transcribe   │ MP3                 │ JSON (segments)     │ S3: /transcripts/ │
│ 3. Segment      │ JSON (segments)     │ JSON (phrases)      │ PostgreSQL        │
│ 4. Classify     │ JSON (phrases)      │ JSON (tagged)       │ PostgreSQL        │
│ 5. Paraphrase   │ JSON (tagged)       │ JSON (final)        │ PostgreSQL        │
│ 6. Generate     │ JSON (phrase pool)  │ JSON (dialogues)    │ PostgreSQL        │
│ 7. Validate     │ JSON (dialogues)    │ JSON (validated)    │ PostgreSQL        │
│ 8. Export       │ JSON (validated)    │ API Response        │ PronIELTS DB      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Error Handling

### 4.1 Retry Strategy

| Stage | Max Retries | Backoff | On Failure |
|-------|-------------|---------|------------|
| Ingest | 3 | Exponential (30s, 60s, 120s) | Mark failed, alert |
| Transcribe | 2 | Fixed (60s) | Mark failed, alert |
| Classify | 5 | Linear (10s) | Skip phrase, log |
| Paraphrase | 5 | Linear (10s) | Use original, flag |
| Generate | 3 | Fixed (30s) | Skip batch, log |
| Export | 3 | Exponential (60s, 120s, 300s) | Queue for retry |

### 4.2 Dead Letter Queue

Failed items are moved to a dead letter queue for manual review:

```json
{
  "dlq_id": "dlq-uuid",
  "stage": "transcribe",
  "episode_id": "yt-abc123xyz",
  "error": "Whisper model OOM error",
  "attempts": 3,
  "last_attempt": "2024-01-15T09:00:00Z",
  "payload": {...}
}
```

---

## 5. Data Quality Metrics

### 5.1 Per-Stage Metrics

| Stage | Success Rate Target | Quality Metric |
|-------|---------------------|----------------|
| Ingest | > 95% | Download completion |
| Transcribe | > 99% | Word error rate < 10% |
| Segment | > 90% | Valid phrases / total segments |
| Classify | > 95% | Confidence score > 0.8 |
| Paraphrase | > 95% | Semantic similarity > 0.85 |
| Generate | > 90% | Validation pass rate |
| Export | > 99% | API success rate |

### 5.2 Quality Checks

```python
# Quality check functions
def check_transcription_quality(transcription):
    avg_confidence = np.mean([
        word["confidence"]
        for seg in transcription["segments"]
        for word in seg.get("words", [])
    ])
    return avg_confidence > 0.85

def check_paraphrase_quality(original, paraphrased):
    # Using sentence transformers for semantic similarity
    similarity = sentence_similarity(original, paraphrased)
    return similarity > 0.75 and similarity < 0.95  # Not too similar, not too different

def check_cefr_consistency(dialogue):
    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    target_idx = levels.index(dialogue["cefr_level"])

    for turn in dialogue["turns"]:
        turn_level = classify_cefr(turn["text"])
        turn_idx = levels.index(turn_level)
        if abs(turn_idx - target_idx) > 1:
            return False
    return True
```

---

## 6. Airflow DAG Structure

```python
# Simplified DAG structure
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

with DAG(
    dag_id="content_processing_pipeline",
    schedule_interval="0 6 * * MON",  # Every Monday at 6 AM
    catchup=False
) as dag:

    ingest = KubernetesPodOperator(
        task_id="ingest_content",
        image="pronielts/ingestor:latest",
        # ...
    )

    transcribe = KubernetesPodOperator(
        task_id="transcribe_audio",
        image="pronielts/transcriber:latest",
        # GPU resources
        # ...
    )

    segment = KubernetesPodOperator(
        task_id="segment_transcription",
        image="pronielts/segmenter:latest",
        # ...
    )

    classify = KubernetesPodOperator(
        task_id="classify_phrases",
        image="pronielts/classifier:latest",
        # GPU resources for Ollama
        # ...
    )

    paraphrase = KubernetesPodOperator(
        task_id="paraphrase_phrases",
        image="pronielts/paraphraser:latest",
        # ...
    )

    generate = KubernetesPodOperator(
        task_id="generate_dialogues",
        image="pronielts/dialogue-generator:latest",
        # ...
    )

    validate = KubernetesPodOperator(
        task_id="validate_dialogues",
        image="pronielts/validator:latest",
        # ...
    )

    export = KubernetesPodOperator(
        task_id="export_to_pronielts",
        image="pronielts/exporter:latest",
        # ...
    )

    # Task dependencies
    ingest >> transcribe >> segment >> classify >> paraphrase >> generate >> validate >> export
```

---

## 7. Monitoring Dashboard

### 7.1 Key Metrics to Track

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PIPELINE MONITORING DASHBOARD                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Episodes This Week: 5          Phrases Generated: 423                      │
│  ████████████████████           ████████████████████████████████            │
│                                                                             │
│  Success Rate by Stage:                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Ingest      ████████████████████████████████████████████████ 100%    │   │
│  │ Transcribe  ███████████████████████████████████████████████  98%     │   │
│  │ Segment     ██████████████████████████████████████████       92%     │   │
│  │ Classify    ███████████████████████████████████████████████  97%     │   │
│  │ Paraphrase  ██████████████████████████████████████████████   95%     │   │
│  │ Generate    ████████████████████████████████████████         88%     │   │
│  │ Export      ████████████████████████████████████████████████ 100%    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  CEFR Distribution:              Category Distribution:                     │
│  A1: ██████ 12%                  Professional: ████████████ 25%             │
│  A2: ██████████ 20%              Travel: ████████ 18%                       │
│  B1: ████████████████ 32%        Restaurant: ██████ 12%                     │
│  B2: ████████████ 24%            General: ██████████ 22%                    │
│  C1: ████ 8%                     Technology: ████████ 15%                   │
│  C2: ██ 4%                       Other: ████ 8%                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
