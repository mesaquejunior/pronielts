# PronIELTS Content Automation - Infrastructure Document

## 1. Overview

This document describes the Kubernetes and Airflow infrastructure for the content automation pipeline, designed to integrate with the existing EKS cluster at `/Users/mesaquejunior/Personal/repositories/Automation/projects/InsigneTech/kubernetes`.

---

## 2. Infrastructure Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           AWS EKS CLUSTER                                        │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │                         EXISTING INFRASTRUCTURE                           │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │   │
│  │  │ Traefik Ingress │  │  PostgreSQL     │  │  Cert-Manager   │            │   │
│  │  │ (traefik-system)│  │  (postgres)     │  │  (cert-manager) │            │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘            │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                      NEW: AUTOMATION INFRASTRUCTURE                        │  │
│  │                                                                            │  │
│  │  ┌──────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    AIRFLOW NAMESPACE                                 │  │  │
│  │  │                                                                      │  │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │  │  │
│  │  │  │  Webserver   │  │  Scheduler   │  │  Triggerer   │                │  │  │
│  │  │  │  (1 replica) │  │  (1 replica) │  │  (1 replica) │                │  │  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘                │  │  │
│  │  │                                                                      │  │  │
│  │  │  ┌──────────────────────────────────────────────────────────────┐    │  │  │
│  │  │  │                   KubernetesExecutor                         │    │  │  │
│  │  │  │   (Spawns pods per task - no persistent workers)             │    │  │  │
│  │  │  └──────────────────────────────────────────────────────────────┘    │  │  │
│  │  │                                                                      │  │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │  │  │
│  │  │  │  Redis       │  │  PostgreSQL  │  │  DAGs PVC    │                │  │  │
│  │  │  │  (broker)    │  │  (metadata)  │  │  (storage)   │                │  │  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘                │  │  │
│  │  └──────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                            │  │
│  │  ┌──────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    OLLAMA NAMESPACE                                  │  │  │
│  │  │                                                                      │  │  │
│  │  │  ┌───────────────────────────────────────────────────────────────┐   │  │  │
│  │  │  │  Ollama Server (GPU Node)                                     │   │  │  │
│  │  │  │  - LLaMA 3.1 8B model                                         │   │  │  │
│  │  │  │  - Mistral 7B (backup)                                        │   │  │  │
│  │  │  │  - GPU: 1x NVIDIA (8GB+ VRAM)                                 │   │  │  │
│  │  │  │  - ClusterIP Service                                          │   │  │  │
│  │  │  └───────────────────────────────────────────────────────────────┘   │  │  │
│  │  └──────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                            │  │
│  │  ┌──────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    MINIO NAMESPACE                                   │  │  │
│  │  │                                                                      │  │  │
│  │  │  ┌───────────────────────────────────────────────────────────────┐   │  │  │
│  │  │  │  MinIO Server                                                 │   │  │  │
│  │  │  │  - Object storage for audio/transcriptions                    │   │  │  │
│  │  │  │  - S3-compatible API                                          │   │  │  │
│  │  │  │  - 100GB persistent volume                                    │   │  │  │
│  │  │  └───────────────────────────────────────────────────────────────┘   │  │  │
│  │  └──────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                            │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                         TASK PODS (Dynamic)                                │  │
│  │                                                                            │  │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐    │  │
│  │  │ Ingestor │  │Transcriber│  │Classifier│  │Paraphraser│  │ Exporter │    │  │
│  │  │   Pod    │  │   Pod     │  │   Pod    │  │   Pod     │  │   Pod    │    │  │
│  │  │          │  │  (GPU)    │  │  (GPU)   │  │  (GPU)    │  │          │    │  │
│  │  └──────────┘  └───────────┘  └──────────┘  └───────────┘  └──────────┘    │  │
│  │                                                                            │  │
│  │  * Pods are created/destroyed per task execution                           │  │
│  │  * GPU pods scheduled to GPU-enabled nodes                                 │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Namespace Structure

```yaml
# Namespaces to create
apiVersion: v1
kind: Namespace
metadata:
  name: airflow
  labels:
    app: pronielts-automation
---
apiVersion: v1
kind: Namespace
metadata:
  name: ollama
  labels:
    app: pronielts-automation
---
apiVersion: v1
kind: Namespace
metadata:
  name: minio
  labels:
    app: pronielts-automation
---
apiVersion: v1
kind: Namespace
metadata:
  name: automation-tasks
  labels:
    app: pronielts-automation
```

---

## 4. Airflow Configuration

### 4.1 Helm Values

```yaml
# airflow-values.yaml
# Apache Airflow Helm Chart Configuration

# Executor type - KubernetesExecutor for dynamic pod creation
executor: "KubernetesExecutor"

# Airflow configuration
config:
  core:
    dags_folder: /opt/airflow/dags
    load_examples: false
    default_timezone: America/Sao_Paulo
    parallelism: 8
    max_active_tasks_per_dag: 4
    max_active_runs_per_dag: 2

  kubernetes:
    namespace: automation-tasks
    worker_container_repository: pronielts/airflow-worker
    worker_container_tag: latest
    delete_worker_pods: true
    delete_worker_pods_on_failure: false
    worker_pods_creation_batch_size: 2

  logging:
    remote_logging: false
    logging_level: INFO

# Webserver configuration
webserver:
  replicas: 1
  resources:
    requests:
      cpu: 100m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi
  service:
    type: ClusterIP
    port: 8080

# Scheduler configuration
scheduler:
  replicas: 1
  resources:
    requests:
      cpu: 100m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi

# Triggerer for deferrable operators
triggerer:
  enabled: true
  replicas: 1
  resources:
    requests:
      cpu: 50m
      memory: 256Mi
    limits:
      cpu: 200m
      memory: 512Mi

# PostgreSQL for Airflow metadata
postgresql:
  enabled: true
  auth:
    username: airflow
    database: airflow
  primary:
    persistence:
      enabled: true
      size: 8Gi
      storageClass: local-path

# Redis for task queue (used by triggerer)
redis:
  enabled: true
  architecture: standalone
  auth:
    enabled: false
  master:
    persistence:
      enabled: false
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        cpu: 100m
        memory: 128Mi

# DAGs configuration
dags:
  persistence:
    enabled: true
    size: 5Gi
    storageClass: local-path
    accessMode: ReadWriteOnce
  gitSync:
    enabled: false  # Will use PVC mounted DAGs

# Logs configuration
logs:
  persistence:
    enabled: true
    size: 10Gi
    storageClass: local-path

# Worker pod template (for KubernetesExecutor)
workers:
  podTemplate:
    spec:
      containers:
        - name: base
          image: pronielts/airflow-worker:latest
          imagePullPolicy: Always
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 2Gi
          volumeMounts:
            - name: dags
              mountPath: /opt/airflow/dags
              readOnly: true
      volumes:
        - name: dags
          persistentVolumeClaim:
            claimName: airflow-dags

# Ingress configuration (using existing Traefik)
ingress:
  enabled: true
  web:
    enabled: true
    annotations:
      kubernetes.io/ingress.class: traefik
      traefik.ingress.kubernetes.io/router.tls: "true"
      cert-manager.io/cluster-issuer: letsencrypt-production
    hosts:
      - name: airflow.insigne.tech
        tls:
          enabled: true
          secretName: airflow-tls-secret
    path: /

# Environment variables
extraEnv:
  - name: AIRFLOW__CORE__FERNET_KEY
    valueFrom:
      secretKeyRef:
        name: airflow-secrets
        key: fernet-key
  - name: OLLAMA_HOST
    value: "http://ollama.ollama.svc.cluster.local:11434"
  - name: MINIO_ENDPOINT
    value: "minio.minio.svc.cluster.local:9000"
```

### 4.2 Airflow Secrets (Terraform)

```hcl
# airflow-secrets.tf

resource "kubernetes_secret" "airflow_secrets" {
  metadata {
    name      = "airflow-secrets"
    namespace = "airflow"
  }

  data = {
    "fernet-key" = base64encode(random_password.fernet_key.result)
    "webserver-secret-key" = base64encode(random_password.webserver_key.result)
  }
}

resource "random_password" "fernet_key" {
  length  = 32
  special = false
}

resource "random_password" "webserver_key" {
  length  = 32
  special = false
}
```

---

## 5. Ollama Configuration

### 5.1 Deployment

```yaml
# ollama-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: ollama
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
        - name: ollama
          image: ollama/ollama:latest
          ports:
            - containerPort: 11434
          resources:
            requests:
              cpu: 500m
              memory: 4Gi
              nvidia.com/gpu: 1  # Request 1 GPU
            limits:
              cpu: 4000m
              memory: 12Gi
              nvidia.com/gpu: 1
          volumeMounts:
            - name: ollama-data
              mountPath: /root/.ollama
          env:
            - name: OLLAMA_HOST
              value: "0.0.0.0:11434"
            - name: OLLAMA_KEEP_ALIVE
              value: "24h"  # Keep models loaded
          readinessProbe:
            httpGet:
              path: /api/version
              port: 11434
            initialDelaySeconds: 30
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /api/version
              port: 11434
            initialDelaySeconds: 60
            periodSeconds: 30
      volumes:
        - name: ollama-data
          persistentVolumeClaim:
            claimName: ollama-pvc
      # Node selector for GPU nodes
      nodeSelector:
        nvidia.com/gpu.present: "true"
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
---
apiVersion: v1
kind: Service
metadata:
  name: ollama
  namespace: ollama
spec:
  selector:
    app: ollama
  ports:
    - port: 11434
      targetPort: 11434
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ollama-pvc
  namespace: ollama
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 50Gi  # Space for models
```

### 5.2 Model Preload Job

```yaml
# ollama-model-preload.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ollama-model-preload
  namespace: ollama
spec:
  template:
    spec:
      containers:
        - name: model-puller
          image: curlimages/curl:latest
          command:
            - /bin/sh
            - -c
            - |
              echo "Waiting for Ollama to be ready..."
              sleep 30
              echo "Pulling LLaMA 3.1 8B model..."
              curl -X POST http://ollama.ollama.svc.cluster.local:11434/api/pull \
                -d '{"name": "llama3.1:8b"}'
              echo "Pulling Mistral 7B model (backup)..."
              curl -X POST http://ollama.ollama.svc.cluster.local:11434/api/pull \
                -d '{"name": "mistral:7b"}'
              echo "Models pulled successfully!"
      restartPolicy: OnFailure
  backoffLimit: 3
```

---

## 6. MinIO Configuration

### 6.1 Deployment

```yaml
# minio-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
  namespace: minio
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
        - name: minio
          image: minio/minio:latest
          command:
            - /bin/bash
            - -c
            - minio server /data --console-address ":9001"
          ports:
            - containerPort: 9000
              name: api
            - containerPort: 9001
              name: console
          resources:
            requests:
              cpu: 100m
              memory: 512Mi
            limits:
              cpu: 500m
              memory: 1Gi
          env:
            - name: MINIO_ROOT_USER
              valueFrom:
                secretKeyRef:
                  name: minio-secrets
                  key: root-user
            - name: MINIO_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: minio-secrets
                  key: root-password
          volumeMounts:
            - name: minio-data
              mountPath: /data
          readinessProbe:
            httpGet:
              path: /minio/health/ready
              port: 9000
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /minio/health/live
              port: 9000
            initialDelaySeconds: 30
            periodSeconds: 30
      volumes:
        - name: minio-data
          persistentVolumeClaim:
            claimName: minio-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: minio
  namespace: minio
spec:
  selector:
    app: minio
  ports:
    - port: 9000
      targetPort: 9000
      name: api
    - port: 9001
      targetPort: 9001
      name: console
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-pvc
  namespace: minio
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 100Gi
```

### 6.2 Bucket Initialization

```yaml
# minio-bucket-init.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: minio-bucket-init
  namespace: minio
spec:
  template:
    spec:
      containers:
        - name: mc
          image: minio/mc:latest
          command:
            - /bin/sh
            - -c
            - |
              echo "Waiting for MinIO to be ready..."
              sleep 15
              mc alias set myminio http://minio.minio.svc.cluster.local:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
              mc mb myminio/pronielts-raw --ignore-existing
              mc mb myminio/pronielts-transcriptions --ignore-existing
              mc mb myminio/pronielts-processed --ignore-existing
              echo "Buckets created successfully!"
          env:
            - name: MINIO_ROOT_USER
              valueFrom:
                secretKeyRef:
                  name: minio-secrets
                  key: root-user
            - name: MINIO_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: minio-secrets
                  key: root-password
      restartPolicy: OnFailure
  backoffLimit: 3
```

---

## 7. Task Pod Templates

### 7.1 Ingestor Pod

```yaml
# pod-template-ingestor.yaml
apiVersion: v1
kind: Pod
metadata:
  name: ingestor-task
  namespace: automation-tasks
spec:
  containers:
    - name: ingestor
      image: pronielts/ingestor:latest
      resources:
        requests:
          cpu: 200m
          memory: 512Mi
        limits:
          cpu: 1000m
          memory: 2Gi
      env:
        - name: MINIO_ENDPOINT
          value: "minio.minio.svc.cluster.local:9000"
        - name: MINIO_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: minio-credentials
              key: access-key
        - name: MINIO_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: minio-credentials
              key: secret-key
      volumeMounts:
        - name: temp-storage
          mountPath: /tmp/downloads
  volumes:
    - name: temp-storage
      emptyDir:
        sizeLimit: 5Gi
  restartPolicy: Never
```

### 7.2 Transcriber Pod (GPU)

```yaml
# pod-template-transcriber.yaml
apiVersion: v1
kind: Pod
metadata:
  name: transcriber-task
  namespace: automation-tasks
spec:
  containers:
    - name: transcriber
      image: pronielts/transcriber:latest
      resources:
        requests:
          cpu: 500m
          memory: 4Gi
          nvidia.com/gpu: 1
        limits:
          cpu: 2000m
          memory: 8Gi
          nvidia.com/gpu: 1
      env:
        - name: WHISPER_MODEL
          value: "medium"
        - name: MINIO_ENDPOINT
          value: "minio.minio.svc.cluster.local:9000"
      volumeMounts:
        - name: temp-storage
          mountPath: /tmp/processing
        - name: whisper-cache
          mountPath: /root/.cache/whisper
  volumes:
    - name: temp-storage
      emptyDir:
        sizeLimit: 10Gi
    - name: whisper-cache
      persistentVolumeClaim:
        claimName: whisper-model-cache
  nodeSelector:
    nvidia.com/gpu.present: "true"
  tolerations:
    - key: nvidia.com/gpu
      operator: Exists
      effect: NoSchedule
  restartPolicy: Never
```

### 7.3 Classifier Pod (Uses Ollama)

```yaml
# pod-template-classifier.yaml
apiVersion: v1
kind: Pod
metadata:
  name: classifier-task
  namespace: automation-tasks
spec:
  containers:
    - name: classifier
      image: pronielts/classifier:latest
      resources:
        requests:
          cpu: 200m
          memory: 1Gi
        limits:
          cpu: 1000m
          memory: 2Gi
      env:
        - name: OLLAMA_HOST
          value: "http://ollama.ollama.svc.cluster.local:11434"
        - name: LLM_MODEL
          value: "llama3.1:8b"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: automation-db-credentials
              key: database-url
  restartPolicy: Never
```

---

## 8. Terraform Structure

### 8.1 File Organization

```
automation/terraform/
├── providers.tf           # Kubernetes, Helm providers
├── variables.tf           # Global variables
├── namespaces.tf          # Namespace definitions
├── airflow-helm.tf        # Airflow Helm release
├── airflow-secrets.tf     # Airflow secrets
├── airflow-ingress.tf     # Airflow ingress (if not in Helm)
├── ollama-deployment.tf   # Ollama deployment
├── ollama-storage.tf      # Ollama PVC
├── minio-deployment.tf    # MinIO deployment
├── minio-storage.tf       # MinIO PVC
├── minio-secrets.tf       # MinIO credentials
├── automation-db.tf       # Automation PostgreSQL schema
├── rbac.tf                # RBAC for task pods
└── outputs.tf             # Output values
```

### 8.2 Sample providers.tf

```hcl
# providers.tf
terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.38.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.17.0"
    }
  }

  backend "s3" {
    bucket = "terraform-state-backend-config-725564869109"
    key    = "state/insignetech/automation/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}
```

---

## 9. Resource Summary

### 9.1 Compute Resources

| Component | Replicas | CPU (req/limit) | Memory (req/limit) | GPU |
|-----------|----------|-----------------|--------------------|----|
| Airflow Webserver | 1 | 100m / 500m | 512Mi / 1Gi | - |
| Airflow Scheduler | 1 | 100m / 500m | 512Mi / 1Gi | - |
| Airflow Triggerer | 1 | 50m / 200m | 256Mi / 512Mi | - |
| Airflow PostgreSQL | 1 | 250m / 500m | 512Mi / 1Gi | - |
| Airflow Redis | 1 | 50m / 100m | 64Mi / 128Mi | - |
| Ollama | 1 | 500m / 4000m | 4Gi / 12Gi | 1 |
| MinIO | 1 | 100m / 500m | 512Mi / 1Gi | - |
| **Total Base** | **7** | **1.15 / 6.3 cores** | **6.4Gi / 17.6Gi** | **1** |

### 9.2 Storage Resources

| Component | Size | Type | Purpose |
|-----------|------|------|---------|
| Airflow PostgreSQL | 8Gi | local-path | Metadata database |
| Airflow DAGs | 5Gi | local-path | DAG files |
| Airflow Logs | 10Gi | local-path | Task logs |
| Ollama Models | 50Gi | local-path | LLM model storage |
| MinIO Data | 100Gi | local-path | Audio and transcriptions |
| Whisper Cache | 10Gi | local-path | Whisper model cache |
| **Total** | **183Gi** | | |

### 9.3 Task Pod Resources (Per Execution)

| Task | CPU (req/limit) | Memory (req/limit) | GPU | Duration (est.) |
|------|-----------------|--------------------|----|-----------------|
| Ingestor | 200m / 1000m | 512Mi / 2Gi | - | 2-5 min |
| Transcriber | 500m / 2000m | 4Gi / 8Gi | 1 | 10-30 min |
| Segmenter | 100m / 500m | 256Mi / 1Gi | - | 1-2 min |
| Classifier | 200m / 1000m | 1Gi / 2Gi | - | 5-15 min |
| Paraphraser | 200m / 1000m | 1Gi / 2Gi | - | 5-15 min |
| Generator | 200m / 1000m | 1Gi / 2Gi | - | 2-5 min |
| Validator | 100m / 500m | 256Mi / 512Mi | - | 1-2 min |
| Exporter | 100m / 500m | 256Mi / 512Mi | - | 1-2 min |

---

## 10. Network Configuration

### 10.1 Service Discovery

| Service | Namespace | DNS Name | Port |
|---------|-----------|----------|------|
| Airflow Web | airflow | airflow-webserver.airflow.svc.cluster.local | 8080 |
| Airflow DB | airflow | airflow-postgresql.airflow.svc.cluster.local | 5432 |
| Ollama | ollama | ollama.ollama.svc.cluster.local | 11434 |
| MinIO API | minio | minio.minio.svc.cluster.local | 9000 |
| MinIO Console | minio | minio.minio.svc.cluster.local | 9001 |
| Automation DB | postgres | postgresql.postgres.svc.cluster.local | 5432 |

### 10.2 Ingress Routes

| Host | Service | TLS |
|------|---------|-----|
| airflow.insigne.tech | airflow-webserver:8080 | Let's Encrypt |
| minio.insigne.tech | minio:9001 | Let's Encrypt |

---

## 11. Deployment Order

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT SEQUENCE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Create Namespaces
    └── airflow, ollama, minio, automation-tasks

Step 2: Deploy Storage
    └── PVCs for Airflow, Ollama, MinIO

Step 3: Deploy Secrets
    └── Airflow secrets, MinIO credentials, DB credentials

Step 4: Deploy MinIO
    └── MinIO server → Bucket initialization job

Step 5: Deploy Ollama
    └── Ollama server → Model preload job

Step 6: Deploy Airflow
    └── Helm install airflow/airflow

Step 7: Configure Ingress
    └── Airflow and MinIO ingress with TLS

Step 8: Initialize Automation DB
    └── Create tables in existing PostgreSQL

Step 9: Deploy DAGs
    └── Copy DAG files to Airflow DAGs PVC

Step 10: Verify
    └── Health checks, test DAG run
```

---

## 12. Monitoring Integration

### 12.1 Metrics Endpoints

| Component | Endpoint | Metrics |
|-----------|----------|---------|
| Airflow | /admin/metrics | DAG runs, task duration, pool usage |
| Ollama | /api/tags | Model status, GPU utilization |
| MinIO | /minio/v2/metrics/cluster | Storage usage, request rates |

### 12.2 Logging

- **Airflow logs:** Persistent volume at `/opt/airflow/logs`
- **Ollama logs:** Container stdout → Kubernetes logs
- **MinIO logs:** Container stdout → Kubernetes logs
- **Task pods:** Logs collected by Airflow, stored in Airflow logs PVC

---

## 13. Disaster Recovery

### 13.1 Backup Strategy

| Component | Backup Method | Frequency | Retention |
|-----------|---------------|-----------|-----------|
| Airflow DB | pg_dump | Daily | 7 days |
| Automation DB | pg_dump | Daily | 30 days |
| MinIO Data | mc mirror | Weekly | 4 weeks |
| DAG Files | Git | On commit | Indefinite |
| Terraform State | S3 versioning | On apply | Indefinite |

### 13.2 Recovery Procedures

1. **Namespace recreation:** `kubectl apply -f namespaces.tf`
2. **Storage restoration:** Restore PVCs from backup
3. **Database restoration:** `pg_restore` from backup
4. **Secret recreation:** `terraform apply` (secrets in state)
5. **Application redeployment:** `terraform apply`
6. **DAG synchronization:** Copy DAGs to PVC
