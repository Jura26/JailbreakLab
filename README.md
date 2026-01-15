# JailbreakLab - Test AI Model Vulnerabilities With Various Attack And Defense Mechanisms

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

**JailbreakLab** is an educational and research-oriented platform designed to:

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
│    Frontend     │────▶│     Backend     │────▶│      Redis      │
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

-  **Docker** & **Docker Compose**
-  (Optional) **NVIDIA GPU** with **CUDA** for faster inference
-  (Optional) **Node.js** 20+ and **Python** 3.10+ for local development

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

| Attack                                  | Description                                                                 |
| --------------------------------------- | --------------------------------------------------------------------------- |
| **None**                                | Baseline – sends prompt without modification                                 |
| **DAN Prompt**                          | Persona-based jailbreak that ignores safety constraints                      |
| **DAN V6**                              | Gamified DAN attack using token penalties to coerce compliance               |
| **DAN V9**                              | Dual-output DAN jailbreak forcing censored and uncensored responses          |
| **DAN V11**                             | Virtual-machine DAN variant redefining rules and content policies            |
| **STAN Prompt**                         | Norm-breaking persona that rejects ethical and safety standards              |
| **Mongo Tom Prompt**                    | Profane persona-based jailbreak using humor and character immersion          |
| **Role Playing**                        | Contextual jailbreak using fictional or authoritative roles                  |
| **Chain of Questions**                  | Multi-turn attack that escalates harmless queries into harmful outcomes      |
| **Bias Guided FCB**                     | Automated jailbreak using feedback-controlled adversarial optimization        |
| **ASCII Art Jailbreak**                 | Obfuscated attack encoding instructions in ASCII art                         |
| **NeuroStrike**                         | Safety-neuron targeting attack exploiting alignment transferability          |
| **GCG (Gradient-Based)**                | Gradient-optimized adversarial suffix jailbreak                              |
| **TAP (Tree of Attacks with Pruning)**  | Tree-based automated jailbreak using branching and pruning                   |
| **PAIR**                                | Iterative black-box jailbreak using attacker–target model interaction        |
| **Crescendo Attack**                    | Gradual multi-turn escalation exploiting conversational commitment           |
| **Base64 Encoded Attack**               | Jailbreak using base64-encoded malicious prompts                             |
| **Base64 + Competing Objective**        | Base64 attack combined with forced positive-response objective               |
| **Ubbi Dubbi Attack**                   | Language-transformation jailbreak via mismatched generalization              |
| **ROT13 Encoded Attack**                | Jailbreak using ROT13-encoded malicious instructions                          |


## 🛡️ Defense Mechanisms

| Defense                                   | Description                                                                  |
| ----------------------------------------- | ---------------------------------------------------------------------------- |
| **None**                                  | Baseline with no defenses enabled                                             |
| **Input Sanitization**                    | Filters malicious patterns and anomalous input structures                     |
| **System Prompt Hardening**               | Enforces strict safety rules via reinforced system instructions               |
| **MaskedDefender**                        | Masks high-risk tokens while preserving benign prompt context                 |
| **PIGuard**                               | ML-based prompt injection detection using semantic analysis                   |
| **Llama Guard 3**                         | Safety classifier for input and output across multiple harm categories        |
| **Llama Guard 4**                         | Enhanced multimodal safety classifier with reduced false positives            |
| **Guardrails: Multi-Turn Injection**      | Detects delayed jailbreaks using conversation history                         |
| **Guardrails: LLM-as-Judge**              | Semantic reasoning defense for subtle or obfuscated attacks                   |
| **Guardrails: Unicode & Obfuscation**     | Detects hidden instructions via encoding and character tricks                 |
| **Guardrails: Role/Persona Enforcement**  | Blocks unsafe role-play and persona-based attacks                              |
| **Guardrails: Tool / Function Safety**    | Prevents unsafe tool or function call instructions                            |
| **Guardrails: Detect Jailbreak**          | Identifies attempts to override or bypass model safety rules                  |
| **Guardrails: Full Defense Stack**        | Combined Guardrails validators for layered protection                          |
| **Semantic Perturbation**                 | Breaks social-engineering flows via synonym substitution                      |
| **Character Perturbation**                | Disrupts adversarial suffixes using character-level noise                     |
| **Hybrid Perturbation**                   | Combines semantic and character smoothing to neutralize diverse jailbreaks    |
| **Hybrid Perturbation (LLM Judge)**       | Multi-sample hybrid smoothing with automated safety-based prompt selection    |


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

## ⚙️ Configuration

### Environment Variables

Create a **.env** inside of ``JailbreakLab/backend/`` folder and set the variables below. Look for ``example.env`` for more detailed info.

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
