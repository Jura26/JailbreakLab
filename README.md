# ProjektR - LLM Security Testing Framework

A comprehensive framework for testing and demonstrating adversarial attacks and defense mechanisms against Large Language Models (LLMs). This project provides an interactive web interface to experiment with various jailbreak attack techniques and evaluate different defense strategies in real-time.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-19.x-61dafb.svg)
![Docker](https://img.shields.io/badge/docker-compose-2496ed.svg)

## 📋 Table of Contents

-  [Overview](#overview)
-  [Features](#features)
-  [Architecture](#architecture)
-  [Quick Start](#quick-start)
-  [Attack Types](#attack-types)
-  [Defense Mechanisms](#defense-mechanisms)
-  [Supported Models](#supported-models)
-  [Project Structure](#project-structure)
-  [Configuration](#configuration)
-  [Development](#development)
-  [Deployment](#deployment)
-  [Contributing](#contributing)

## 🎯 Overview

ProjektR is an educational and research-oriented platform designed to:

-  **Demonstrate** how various prompt injection and jailbreak attacks work against LLMs
-  **Evaluate** the effectiveness of different defense mechanisms
-  **Compare** model robustness across different architectures and sizes
-  **Educate** developers and researchers about LLM security vulnerabilities

## ✨ Features

-  🖥️ **Interactive Web Interface** - Modern React-based UI with real-time streaming responses
-  ⚔️ **Multiple Attack Vectors** - DAN prompts, role-playing, chain-of-questions, ASCII art jailbreaks, and more
-  🛡️ **Layered Defenses** - Input sanitization, output filtering, neural MaskedDefender, and more
-  🤖 **Multi-Model Support** - Test against GPT-2 variants, OPT, Mistral, LLaMA, and other HuggingFace models
-  📊 **Progress Tracking** - Real-time progress indicators during model inference
-  💾 **Session History** - Redis-backed conversation caching
-  🐳 **Containerized** - Full Docker Compose setup for easy deployment
-  ☸️ **Kubernetes Ready** - K8s manifests for production deployment

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │───▶│     Backend     │───▶│      Redis      │
│  (React + Vite) │     │    (FastAPI)    │     │  (Session Cache)│
│    Port 5173    │     │    Port 8000    │     │    Port 6379    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  HuggingFace    │
                        │     Models      │
                        │  (GPU/CPU)      │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

-  Docker & Docker Compose
-  (Optional) NVIDIA GPU with CUDA for faster inference
-  (Optional) Node.js 20+ and Python 3.10+ for local development

### Running with Docker Compose

```bash
# Clone the repository
git clone https://github.com/karloks2005/ProjektR.git
cd ProjektR

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
```

### Running Locally (Development)

**Backend:**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

**Redis:**

```bash
docker run -d -p 6379:6379 redis:7
```

## ⚔️ Attack Types

| Attack                  | Description                                                                                    |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| **None**                | Baseline - sends prompt without modification                                                   |
| **DAN Prompt**          | "Do Anything Now" persona-based jailbreak that instructs the model to ignore safety guidelines |
| **Role Playing**        | Social engineering attack using false identities to manipulate model behavior                  |
| **Chain of Questions**  | Multi-turn attack that breaks harmful requests into innocent-looking sub-questions             |
| **Bias Guided FCB**     | Automated optimization attack using feedback-controlled branching                              |
| **ASCII Art Jailbreak** | Encodes malicious instructions in ASCII art to bypass text-based filters                       |

## 🛡️ Defense Mechanisms

| Defense                     | Description                                                                     |
| --------------------------- | ------------------------------------------------------------------------------- |
| **None**                    | No protection - baseline for comparison                                         |
| **Input Sanitization**      | Filters malicious patterns, keywords, and anomalies before processing           |
| **Output Filtering**        | Monitors generated content for harmful or inappropriate responses               |
| **MaskedDefender**          | Neural network-based defense that masks harmful tokens while preserving context |
| **System Prompt Hardening** | Adds strong system prompts to restrict model behavior and improve safety        |

## 🤖 Supported Models

The framework supports various HuggingFace models:

| Model        | Parameters | VRAM Required |
| ------------ | ---------- | ------------- |
| GPT-2 Small  | 124M       | ~1 GB         |
| GPT-2 Medium | 355M       | ~1.5 GB       |
| GPT-2 Large  | 774M       | ~3-4 GB       |
| GPT-2 XL     | 1.5B       | ~6-8 GB       |
| OPT-2.7B     | 2.7B       | ~14 GB        |
| OPT-6.7B     | 6.7B       | ~20 GB        |
| OPT-13B      | 13B        | ~32 GB        |
| Mistral-7B   | 7B         | ~12 GB        |
| LLaMA 2-7B   | 7B         | ~14 GB        |

## 📁 Project Structure

```
ProjektR/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── model.py                # Model loading and inference
│   ├── history_cache.py        # Redis-backed session management
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile
│   ├── attacks/
│   │   ├── promptInjection.py  # Attack execution engine
│   │   └── FCB.py              # Feedback-controlled branching attack
│   └── defenses/
│       ├── defense_manager.py  # Defense orchestration
│       ├── input_sanitization.py
│       ├── output_filtering.py
│       └── MaskedDefender/     # Neural defense model
│           ├── masked_defender.py
│           └── masked_defender.pth
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main React application
│   │   └── components/
│   │       ├── attacks.tsx     # Attack definitions & metadata
│   │       ├── defenses.tsx    # Defense definitions & metadata
│   │       └── models.tsx      # Model configurations
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── k8s/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── redis-deployment.yaml
├── docker-compose.yml
└── README.md
```

## ⚙️ Configuration

### Environment Variables

| Variable                 | Default                | Description               |
| ------------------------ | ---------------------- | ------------------------- |
| `REDIS_URL`              | `redis://redis:6379/0` | Redis connection URL      |
| `TRANSFORMERS_VERBOSITY` | `error`                | HuggingFace logging level |

### Backend Configuration

Model inference settings can be adjusted in `backend/model.py`. Defense sensitivity thresholds are configurable in `backend/defenses/`.

### Frontend Configuration

The frontend connects to the backend at `http://localhost:8000` by default. Modify the API URL in `frontend/src/App.tsx` for different environments.

## 🛠️ Development

### Adding New Attacks

1. Create a new attack handler in `backend/attacks/`
2. Register it in `backend/main.py` under `PROMPT_INJECTION_ATTACKS`
3. Add UI metadata in `frontend/src/components/attacks.tsx`

### Adding New Defenses

1. Implement the defense function in `backend/defenses/`
2. Register it in `backend/defenses/defense_manager.py` under `DEFENSES`
3. Add UI metadata in `frontend/src/components/defenses.tsx`

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run lint
```

## 🚢 Deployment

### Kubernetes Deployment

```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
```

### Google Cloud Deployment

Refer to the `gcloud` and `kubectl` configuration files for GKE deployment instructions.

## 📚 References

-  [LLM Attacks Catalog](https://llm-attacks.org/)
-  [Universal and Transferable Adversarial Attacks on Aligned Language Models](https://arxiv.org/abs/2307.02483)
-  [Jailbroken: How Does LLM Safety Training Fail?](https://arxiv.org/abs/2302.04237)
-  [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
-  [Prompt Injection Explained](https://simonwillison.net/2023/May/2/prompt-injection-explained/)

## ⚠️ Disclaimer

This framework is intended for **educational and research purposes only**. The attack techniques demonstrated should only be used to test and improve the security of AI systems you own or have permission to test. Misuse of these techniques may violate laws and terms of service.
