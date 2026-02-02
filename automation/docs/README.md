# PronIELTS Content Automation - Documentation

## Overview

This documentation describes the content automation pipeline that extracts, transcribes, and transforms English audio content from multiple sources (YouTube, podcasts, Spotify) into structured learning materials for the PronIELTS platform.

## Documentation Index

| Document | Description |
|----------|-------------|
| [architecture.md](architecture.md) | High-level system architecture, technology stack, data models, and design decisions |
| [data_flow.md](data_flow.md) | Detailed data flow through each pipeline stage with schemas and examples |
| [infrastructure.md](infrastructure.md) | Kubernetes and Airflow infrastructure configuration |
| [integration.md](integration.md) | API contracts and integration with PronIELTS platform |

## Quick Links

### Architecture
- [System Overview](architecture.md#2-high-level-architecture)
- [Technology Stack](architecture.md#4-technology-stack)
- [Data Models](architecture.md#5-data-models)
- [Cost Analysis](architecture.md#10-cost-analysis)

### Data Flow
- [Pipeline Stages](data_flow.md#2-stage-details)
- [Transcription Output](data_flow.md#22-stage-2-transcription)
- [CEFR Classification](data_flow.md#24-stage-4-cefr-classification)
- [Dialogue Generation](data_flow.md#26-stage-6-dialogue-generation)

### Infrastructure
- [Kubernetes Architecture](infrastructure.md#2-infrastructure-architecture)
- [Airflow Configuration](infrastructure.md#4-airflow-configuration)
- [Ollama (LLM) Setup](infrastructure.md#5-ollama-configuration)
- [Resource Requirements](infrastructure.md#9-resource-summary)

### Integration
- [Bulk Import API](integration.md#3-bulk-import-api-specification)
- [Data Mapping](integration.md#4-data-mapping)
- [Backend Implementation](integration.md#5-backend-implementation-guide)
- [Rollout Plan](integration.md#10-rollout-plan)

## Key Features

- **Multi-source ingestion**: YouTube, Spotify, RSS feeds, Apple Podcasts
- **AI transcription**: OpenAI Whisper (open-source, local)
- **CEFR classification**: LLaMA 3.1 via Ollama (open-source, local)
- **Copyright compliance**: Automatic paraphrasing of all content
- **Accent diversity**: American, British, Australian, South African, Irish, Scottish
- **Kubernetes-native**: Runs on existing EKS cluster with Airflow orchestration

## Technology Stack

| Component | Technology | License |
|-----------|------------|---------|
| Orchestration | Apache Airflow | Apache 2.0 |
| Transcription | OpenAI Whisper | MIT |
| LLM | Ollama + LLaMA 3.1 | MIT / Llama 3 Community |
| Container | Kubernetes (EKS) | Apache 2.0 |
| Storage | MinIO (S3-compatible) | AGPL |
| Database | PostgreSQL | PostgreSQL License |

## Getting Started

1. Review the [Architecture Document](architecture.md) for system overview
2. Understand the [Data Flow](data_flow.md) through the pipeline
3. Set up [Infrastructure](infrastructure.md) on your Kubernetes cluster
4. Implement [Integration](integration.md) endpoints in PronIELTS

## Estimated Resources

- **Storage**: ~183GB for models, audio, and transcriptions
- **Memory**: ~18GB RAM for all services
- **GPU**: 1x NVIDIA GPU (8GB+ VRAM) for Whisper and Ollama
- **Cost**: $0/month (all open-source, local infrastructure)

## Contact

For questions about this documentation, refer to the main PronIELTS repository.


---

## Solution Summary

### Processing Pipeline

```
┌─────────────────┐    ┌──────────┐    ┌─────────┐    ┌──────────────┐
│     Sources     │───▶│ Download │───▶│ Whisper │───▶│ Segmentation │
│ YouTube/Spotify │    └──────────┘    └─────────┘    └──────────────┘
│      RSS        │                                           │
└─────────────────┘                                           ▼
                                                   ┌─────────────────┐
┌─────────────────┐    ┌───────────┐    ┌────────┐ │     Ollama      │
│  PronIELTS API  │◀───│ Dialogues │◀───│Paraph- │◀│ (CEFR + Category│
└─────────────────┘    └───────────┘    │ rase   │ │  Classification)│
                                        └────────┘ └─────────────────┘
```

### Architecture Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Transcription | Whisper (local) | Free, high quality |
| LLM | Ollama + LLaMA 3.1 8B | Zero cost, local execution |
| Orchestration | Airflow + KubernetesExecutor | Isolated container per task |
| Storage | MinIO (S3-compatible) | Open-source, already compatible |
| Integration | Bulk API (REST) | Simplicity for low volume |
| Copyright | Automatic paraphrasing | Legal compliance |

### Required Resources

| Resource | Specification |
|----------|---------------|
| **GPU** | 1x NVIDIA (8GB+ VRAM) |
| **RAM** | ~18GB for base services |
| **Storage** | ~183GB (models + audio + data) |
| **Monthly Cost** | $0 (all local/open-source) |

### Next Steps

- [ ] **Backend PronIELTS**: Implement `/api/v1/admin/bulk-import` endpoint
- [ ] **Terraform**: Create modules for Airflow, Ollama, MinIO
- [ ] **Airflow DAGs**: Develop processing DAGs
- [ ] **Containers**: Build Docker images for each stage
- [ ] **Testing**: End-to-end testing with real content

> **Note:** Documentation files are located in `automation/docs/`.
