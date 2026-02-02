# PronIELTS Content Automation - Hardware Requirements

## 1. Target Hardware Specifications

### Development Environment (Mac Studio M2 Max)

| Component | Specification |
|-----------|---------------|
| CPU | Apple M2 Max 12-core |
| RAM | 32GB Unified Memory |
| GPU | Integrated (38-core GPU + Neural Engine) |
| Storage | Internal SSD |

### Production Cluster (Kubernetes)

| Node | CPU | RAM | Storage | Role |
|------|-----|-----|---------|------|
| RPi5 #1 | ARM Cortex-A76 2.4GHz (4 cores) | 16GB | 256GB NVMe | Worker (Whisper) |
| RPi5 #2 | ARM Cortex-A76 2.4GHz (4 cores) | 16GB | 256GB NVMe | Worker (Ollama) |
| RPi5 #3 | ARM Cortex-A76 2.4GHz (4 cores) | 16GB | 256GB NVMe | Services (Airflow, MinIO) |
| APU1C4 | AMD T40E 1GHz (2 cores) | 4GB | - | Control Plane / Ingress only |

---

## 2. Adjusted Software Stack for ARM64

### Transcription: whisper.cpp (Instead of OpenAI Whisper)

**Reason:** whisper.cpp is optimized for ARM64 and runs 2-3x faster than Python Whisper on Raspberry Pi.

| Model | Size | RAM Usage | Speed on RPi5 | Quality | Recommendation |
|-------|------|-----------|---------------|---------|----------------|
| tiny | 75MB | ~400MB | 0.15 RTF | Basic | Quick tests |
| tiny.en | 75MB | ~400MB | 0.12 RTF | Better (English) | **Development** |
| base | 142MB | ~700MB | 0.25 RTF | Good | Fast processing |
| base.en | 142MB | ~700MB | 0.20 RTF | Better (English) | **Recommended** |
| small | 466MB | ~2GB | 0.45 RTF | Very Good | Quality focus |
| small.en | 466MB | ~2GB | 0.40 RTF | Very Good (English) | **Best balance** |
| medium | 1.5GB | ~5GB | 1.2 RTF | Excellent | ❌ Too slow |

**RTF = Real-Time Factor** (1.0 = real-time, lower is faster)

**Selected Model for Production:** `small.en`
- ~2.5x faster than real-time on RPi5
- Good quality for podcast/interview content
- ~2GB RAM usage

### LLM: Ollama with Smaller Models

**Performance on Raspberry Pi 5 16GB:**

| Model | Size | RAM | Tokens/sec | Quality | Use Case |
|-------|------|-----|------------|---------|----------|
| tinyllama:1.1b | 637MB | ~1.5GB | 10-15 | Basic | Quick classification |
| gemma2:2b | 1.6GB | ~3GB | 6-10 | Good | **Classification** |
| phi3:3.8b | 2.3GB | ~4GB | 4-6 | Very Good | **Paraphrasing** |
| llama3.2:3b | 2.0GB | ~4GB | 4-6 | Very Good | Alternative |
| mistral:7b | 4.1GB | ~8GB | 2-3 | Excellent | ❌ Too slow |
| llama3.1:8b | 4.7GB | ~9GB | 1-2 | Excellent | ❌ Too slow |

**Selected Models:**
- **Classification:** `gemma2:2b` (good quality, fast enough)
- **Paraphrasing:** `phi3:3.8b` (better text generation)

---

## 3. Node Assignment Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLUSTER NODE ASSIGNMENT                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  APU1C4 (Control Plane - DO NOT use for ML workloads)                       │
│  ├── Kubernetes API Server                                                  │
│  ├── etcd                                                                   │
│  ├── Traefik Ingress Controller                                             │
│  └── cert-manager                                                           │
│                                                                             │
│  Labels: node-role.kubernetes.io/control-plane=true                         │
│  Taints: node-role.kubernetes.io/control-plane:NoSchedule                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Raspberry Pi 5 #1 (Transcription Worker)                                   │
│  ├── Whisper.cpp server (persistent)                                        │
│  └── Transcription task pods                                                │
│                                                                             │
│  Labels: workload=transcription, node-type=rpi5                             │
│  Reserved: 4GB RAM for whisper model + 2GB for OS                           │
│  Available for tasks: ~10GB                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Raspberry Pi 5 #2 (LLM Worker)                                             │
│  ├── Ollama server (persistent)                                             │
│  │   ├── gemma2:2b (classification)                                         │
│  │   └── phi3:3.8b (paraphrasing)                                           │
│  └── Classification/Paraphrasing task pods                                  │
│                                                                             │
│  Labels: workload=llm, node-type=rpi5                                       │
│  Reserved: 8GB RAM for Ollama + 2GB for OS                                  │
│  Available for tasks: ~6GB                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Raspberry Pi 5 #3 (Services)                                               │
│  ├── Airflow (webserver, scheduler, triggerer)                              │
│  ├── PostgreSQL (Airflow metadata + Automation data)                        │
│  ├── MinIO (object storage)                                                 │
│  └── General task pods (ingest, export)                                     │
│                                                                             │
│  Labels: workload=services, node-type=rpi5                                  │
│  Reserved: 6GB RAM for services + 2GB for OS                                │
│  Available for tasks: ~8GB                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Adjusted Resource Specifications

### Base Services

| Component | CPU (req/limit) | Memory (req/limit) | Node |
|-----------|-----------------|--------------------|----|
| Airflow Webserver | 50m / 200m | 256Mi / 512Mi | RPi5 #3 |
| Airflow Scheduler | 50m / 200m | 256Mi / 512Mi | RPi5 #3 |
| Airflow Triggerer | 25m / 100m | 128Mi / 256Mi | RPi5 #3 |
| PostgreSQL | 100m / 500m | 512Mi / 1Gi | RPi5 #3 |
| MinIO | 50m / 200m | 256Mi / 512Mi | RPi5 #3 |
| Whisper.cpp Server | 500m / 2000m | 2Gi / 4Gi | RPi5 #1 |
| Ollama Server | 500m / 3000m | 4Gi / 8Gi | RPi5 #2 |

**Total Base Load:**
- RPi5 #1: ~4GB RAM
- RPi5 #2: ~8GB RAM
- RPi5 #3: ~2.5GB RAM

### Task Pods

| Task | CPU (req/limit) | Memory (req/limit) | Duration | Node |
|------|-----------------|--------------------|---------|----|
| Ingestor | 100m / 500m | 256Mi / 512Mi | 2-5 min | RPi5 #3 |
| Transcriber | 100m / 500m | 256Mi / 512Mi | 15-45 min* | RPi5 #1 |
| Segmenter | 50m / 200m | 128Mi / 256Mi | 1-2 min | Any |
| Classifier | 100m / 500m | 256Mi / 512Mi | 10-30 min* | RPi5 #2 |
| Paraphraser | 100m / 500m | 256Mi / 512Mi | 10-30 min* | RPi5 #2 |
| Generator | 100m / 500m | 256Mi / 512Mi | 5-10 min* | RPi5 #2 |
| Validator | 50m / 200m | 128Mi / 256Mi | 1-2 min | Any |
| Exporter | 50m / 200m | 128Mi / 256Mi | 1-2 min | RPi5 #3 |

*Times are longer than original estimates due to ARM64 CPU-only processing.

---

## 5. Storage Allocation

| Volume | Size | Node | Purpose |
|--------|------|------|---------|
| PostgreSQL Data | 20Gi | RPi5 #3 | Database |
| MinIO Data | 100Gi | RPi5 #3 | Audio/Transcriptions |
| Airflow DAGs | 5Gi | RPi5 #3 | DAG files |
| Airflow Logs | 10Gi | RPi5 #3 | Task logs |
| Whisper Models | 5Gi | RPi5 #1 | Model cache |
| Ollama Models | 20Gi | RPi5 #2 | LLM models |

**Total Storage Used:** ~160Gi
**Available per node:** 256Gi
**Remaining:** ~580Gi for raw audio and backups

---

## 6. Performance Expectations

### Processing Time per Episode (30 min podcast)

| Stage | Mac Studio M2 Max | Raspberry Pi 5 Cluster |
|-------|-------------------|------------------------|
| Download | 1-2 min | 1-2 min |
| Transcription | 3-5 min | 12-20 min |
| Segmentation | <1 min | 1-2 min |
| Classification | 5-10 min | 15-30 min |
| Paraphrasing | 5-10 min | 15-30 min |
| Dialogue Generation | 2-5 min | 5-10 min |
| Validation | <1 min | 1-2 min |
| Export | <1 min | <1 min |
| **Total** | **~20-35 min** | **~50-90 min** |

### Throughput

| Environment | Episodes/Day | Episodes/Week |
|-------------|--------------|---------------|
| Mac Studio | ~40-70 | ~300-500 |
| RPi5 Cluster | ~15-25 | ~100-175 |

**For your target of 1-5 episodes/week:** ✅ Both environments are more than sufficient.

---

## 7. Thermal Management

### Raspberry Pi 5 Recommendations

The Raspberry Pi 5 will thermal throttle under sustained ML workloads. Recommendations:

1. **Active Cooling Required**
   - Use official Raspberry Pi Active Cooler or equivalent
   - Target: Keep CPU below 70°C under load

2. **Fan Control**
   ```bash
   # /boot/firmware/config.txt
   dtparam=fan_temp0=50000      # Fan on at 50°C
   dtparam=fan_temp0_hyst=5000  # 5°C hysteresis
   dtparam=fan_temp0_speed=75   # 75% speed at threshold
   ```

3. **Overclocking (Optional, for more performance)**
   ```bash
   # /boot/firmware/config.txt - Only with good cooling!
   arm_freq=2800         # 2.8GHz (default 2.4GHz)
   over_voltage_delta=50000
   ```

4. **Monitoring**
   ```bash
   # Check temperature
   vcgencmd measure_temp

   # Check throttling
   vcgencmd get_throttled
   ```

---

## 8. Development vs Production Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     RECOMMENDED WORKFLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────┐
│         MAC STUDIO M2 MAX            │
│                                      │
│  • Develop and test DAGs             │
│  • Test whisper.cpp locally          │
│  • Test Ollama locally               │
│  • Build and push Docker images      │
│  • Process urgent/batch content      │
│  • Debug pipeline issues             │
│                                      │
│  Models:                             │
│  • Whisper: medium or large-v3       │
│  • Ollama: llama3.1:8b               │
└──────────────────────────────────────┘
              │
              │ Push images & DAGs
              ▼
┌──────────────────────────────────────┐
│       RASPBERRY PI 5 CLUSTER         │
│                                      │
│  • Run scheduled automated jobs      │
│  • Process background content        │
│  • Continuous integration            │
│  • Lower quality but automated       │
│                                      │
│  Models:                             │
│  • Whisper: small.en (whisper.cpp)   │
│  • Ollama: gemma2:2b, phi3:3.8b      │
└──────────────────────────────────────┘
              │
              │ Export to API
              ▼
┌──────────────────────────────────────┐
│          PRONIELTS BACKEND           │
│                                      │
│  • Receive bulk imports              │
│  • Serve mobile/web apps             │
└──────────────────────────────────────┘
```

---

## 9. APU1C4 Configuration

The APU1C4 should NOT run ML workloads. Configure it for infrastructure only:

### Role: Control Plane + Ingress

```yaml
# Node labels
kubectl label node apu1c4 node-role.kubernetes.io/control-plane=true
kubectl label node apu1c4 node-type=apu

# Taint to prevent ML workloads
kubectl taint node apu1c4 node-role.kubernetes.io/control-plane:NoSchedule

# Only allow specific workloads
kubectl label node apu1c4 workload=infrastructure
```

### Workloads Allowed on APU1C4
- Kubernetes control plane (if running k3s server)
- Traefik ingress controller (very light)
- cert-manager (very light)
- CoreDNS

### Workloads NOT Allowed on APU1C4
- Airflow
- PostgreSQL
- MinIO
- Any ML workload
- Any task pod

---

## 10. AI Accelerators for Raspberry Pi 5

The Raspberry Pi 5 lacks a dedicated GPU, but several AI accelerator HATs can significantly improve ML performance.

### 10.1 Available Accelerators Comparison

| Accelerator | NPU | TOPS | Dedicated RAM | Price | Whisper | LLM |
|-------------|-----|------|---------------|-------|---------|-----|
| [AI HAT+ (Hailo-8L)](https://www.raspberrypi.com/products/ai-kit/) | Hailo-8L | 13 | None | ~$70 | ✅ Good | ❌ No |
| [AI HAT+ (Hailo-8)](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html) | Hailo-8 | 26 | None | ~$110 | ✅ Very Good | ⚠️ Limited |
| [AI HAT+ 2 (Hailo-10H)](https://www.raspberrypi.com/news/introducing-the-raspberry-pi-ai-hat-plus-2-generative-ai-on-raspberry-pi-5/) | Hailo-10H | 40 | **8GB LPDDR4** | ~$150 | ✅ Excellent | ✅ Up to 1.5B |
| [Coral M.2 TPU](https://pineboards.io/products/hat-ai-coral-edge-tpu-bundle-for-raspberry-pi-5) | Edge TPU | 4 | None | ~$60+HAT | ❌ Not supported | ❌ No |
| [Coral Dual TPU](https://pineboards.io/products/hat-ai-dual-edge-coral-tpu-bundle-for-raspberry-pi-5) | 2x Edge TPU | 8 | None | ~$100 | ❌ Not supported | ❌ No |

### 10.2 Recommended: Raspberry Pi AI HAT+ 2 (Hailo-10H)

The **AI HAT+ 2** is the best option for this pipeline's use case (Whisper + LLM):

```
┌─────────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI AI HAT+ 2                       │
├─────────────────────────────────────────────────────────────────┤
│  NPU: Hailo-10H                                                 │
│  Performance: 40 TOPS (INT4)                                    │
│  RAM: 8GB LPDDR4 dedicated (does not use Pi's RAM!)             │
│  Power: ~2.5W during inference                                  │
│  Interface: PCIe via M.2 slot                                   │
│                                                                 │
│  Supported Models:                                              │
│  ✅ Whisper-Base (transcription)                                │
│  ✅ Llama-3.2-3B-Instruct (LLM up to 1.5B on-chip)              │
│  ✅ Qwen2.5-VL-3B (vision + language)                           │
│  ✅ Computer vision models (YOLO, etc.)                         │
└─────────────────────────────────────────────────────────────────┘
```

**Key Advantage:** The 8GB dedicated RAM allows running LLMs without consuming the Pi's main memory.

### 10.3 Performance with AI HAT+ 2

Based on benchmarks from [Hackster.io](https://www.hackster.io/news/hailo-demonstrates-accelerated-llm-based-speech-recognition-on-the-raspberry-pi-ai-hat-63eec0214603), [Hailo Community](https://community.hailo.ai/t/real-time-asr-on-raspberry-pi-hailo8l-with-whisper/17936), and [Jeff Geerling](https://www.jeffgeerling.com/blog/2026/raspberry-pi-ai-hat-2/):

| Metric | Without HAT (CPU) | With AI HAT+ 2 | Improvement |
|--------|-------------------|----------------|-------------|
| Whisper inference (30 min audio) | 12-20 min | 2-4 min | **5-6x faster** |
| Computer vision | 1x baseline | 10x faster | **10x faster** |
| LLM (1.5B params) | 2-4 tokens/sec | 8-15 tokens/sec | **3-4x faster** |
| Additional power draw | - | +2.5W | Minimal |

### 10.4 Cluster Configuration with AI HAT+ 2

**Recommended Setup: 2x AI HAT+ 2**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  CLUSTER WITH AI HAT+ 2 (2 units)                           │
└─────────────────────────────────────────────────────────────────────────────┘

  RPi5 #1 + AI HAT+ 2                RPi5 #2 + AI HAT+ 2
  ┌─────────────────────┐            ┌─────────────────────┐
  │  TRANSCRIPTION      │            │  LLM + PARAPHRASE   │
  │                     │            │                     │
  │  Whisper-Base on NPU│            │  Llama-3.2-1B on NPU│
  │  ~5-6x faster       │            │  ~3-4x faster       │
  │                     │            │                     │
  │  Time per episode:  │            │  Time per episode:  │
  │  12-20min → 2-4min  │            │  30min → 8-12min    │
  └─────────────────────┘            └─────────────────────┘

  RPi5 #3 (No HAT needed)
  ┌─────────────────────┐
  │  SERVICES           │
  │                     │
  │  Airflow, MinIO     │
  │  PostgreSQL         │
  │  Backup worker      │
  └─────────────────────┘
```

### 10.5 Performance Comparison: With vs Without AI HAT+ 2

**Processing Time per Episode (30 min podcast):**

| Stage | CPU Only | With AI HAT+ 2 |
|-------|----------|----------------|
| Download | 1-2 min | 1-2 min |
| Transcription | 12-20 min | **2-4 min** |
| Segmentation | 1-2 min | 1-2 min |
| Classification | 15-30 min | **5-10 min** |
| Paraphrasing | 15-30 min | **5-10 min** |
| Dialogue Generation | 5-10 min | **2-5 min** |
| Validation | 1-2 min | 1-2 min |
| Export | <1 min | <1 min |
| **Total** | **50-90 min** | **~15-25 min** |

**Throughput Comparison:**

| Configuration | Episodes/Day | Episodes/Week |
|---------------|--------------|---------------|
| CPU only | 15-25 | 100-175 |
| **With 2x AI HAT+ 2** | **50-80** | **350-550** |

### 10.6 Alternative: AI HAT+ (26 TOPS) - Budget Option

If the AI HAT+ 2 is unavailable or too expensive:

| Feature | AI HAT+ (26 TOPS) | AI HAT+ 2 (40 TOPS) |
|---------|-------------------|---------------------|
| Price | ~$110 | ~$150 |
| TOPS | 26 | 40 |
| Dedicated RAM | None | 8GB |
| Whisper acceleration | ✅ Yes | ✅ Yes |
| LLM acceleration | ⚠️ Limited | ✅ Yes (up to 1.5B) |

**Recommendation:** The 26 TOPS version still provides significant Whisper acceleration and frees the CPU for other tasks. LLMs would continue to run on CPU.

### 10.7 NOT Recommended: Google Coral TPU

The [Google Coral Edge TPU](https://pineboards.io/products/hat-ai-coral-edge-tpu-bundle-for-raspberry-pi-5) is **not suitable** for this pipeline:

| Issue | Details |
|-------|---------|
| No Whisper support | Coral only runs TensorFlow Lite models |
| No LLM support | Cannot run language models |
| Python compatibility | Only supports Python 3.6-3.9 (Pi OS uses 3.11) |
| Limited models | Only computer vision models (YOLO, MobileNet) |
| Best use case | Frigate NVR, camera object detection |

### 10.8 Investment Analysis

| Configuration | Hardware Cost | Performance Gain | ROI |
|---------------|---------------|------------------|-----|
| 2x AI HAT+ 2 | ~$300 | 3-4x faster | Best for serious use |
| 2x AI HAT+ (26T) | ~$220 | 2-3x faster (Whisper only) | Good balance |
| 1x AI HAT+ 2 | ~$150 | 2x faster (one node) | Minimum viable |
| No accelerator | $0 | Baseline | Sufficient for 1-5/week |

### 10.9 Where to Buy

| Store | Products | Link |
|-------|----------|------|
| Raspberry Pi Official | AI HAT+, AI HAT+ 2 | [raspberrypi.com](https://www.raspberrypi.com/products/ai-kit/) |
| Amazon US | AI HAT+ 13T/26T | [Amazon](https://www.amazon.com/HAT-Accelerator-Applications-High-Performance-RPi/dp/B0DLKBL8D9) |
| CanaKit | AI Kit (older) | [canakit.com](https://www.canakit.com/raspberry-pi-ai-kit.html) |
| Pineboards | Coral bundles | [pineboards.io](https://pineboards.io/products/hat-ai-coral-edge-tpu-bundle-for-raspberry-pi-5) |

### 10.10 Software Integration Notes

**Hailo SDK Requirements:**
- Raspberry Pi OS (64-bit) with kernel 6.1+
- Hailo runtime and HailoRT libraries
- Python 3.9+ supported

**Installation:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Hailo runtime (auto-detected on recent Pi OS)
sudo apt install hailo-all

# Verify installation
hailortcli fw-control identify
```

**Whisper on Hailo:**
- Use Hailo Model Zoo's Whisper implementation
- Hybrid mode: encoder on NPU, decoder on CPU
- Achieves ~250ms refresh for live captioning

---

## 11. Other Upgrade Options

### Option 1: Additional RPi5 Node (~$150)
- Add 4th RPi5 for parallel processing
- Dedicated node for specific workloads
- Better resource isolation
- No AI acceleration, but more CPU cores

### Option 2: Mini PC with NVIDIA GPU (~$500-800)
- Intel NUC or similar with NVIDIA GPU
- Full CUDA support for Whisper and Ollama
- Significant performance improvement
- Best long-term option for heavy workloads
- Examples: NVIDIA Jetson Orin Nano (~$500), Mini PC with RTX 3050 (~$700)

### Option 3: Cloud Burst (Variable Cost)
- Use cloud GPU instances for batch processing
- AWS g4dn.xlarge: ~$0.50/hour
- Process large backlogs quickly
- Return to local processing for steady state
