---
title: Ai Security Auditor Environment Server
emoji: 🛡️
colorFrom: red
colorTo: black
sdk: docker
pinned: false
app_port: 7860
base_path: /web
tags:
  - openenv
  - security
  - cybersecurity
---

# AI Security Auditor Environment

A real-world simulation environment where AI agents act as security researchers to identify vulnerabilities in a codebase. The environment provides a structured way for agents to explore files and submit vulnerability reports, which are then programmatically graded.

> 🤗 **Live Demo:** [Hugging Face Space](https://huggingface.co/spaces/MITHUNSHRI/AI-Security-Auditor)

## Overview

The AI Security Auditor presents the agent with several tasks of increasing difficulty:
1. **Secret Detection (Easy)**: Identify hardcoded credentials in configuration files.
2. **SQL Injection (Medium)**: Find unsanitized user input used in database queries.
3. **Path Traversal (Hard)**: Discover insecure file handling that allows unauthorized access.

---

## Quick Start

```python
from AI_SECURITY_AUDITOR import AiSecurityAuditorAction, AiSecurityAuditorEnv
from AI_SECURITY_AUDITOR.models import VulnerabilityReport

with AiSecurityAuditorEnv(base_url="http://localhost:7860") as env:
    # 1. Start the audit
    result = env.reset()
    print(f"Task: {result.observation.message}")

    # 2. Explore the codebase
    result = env.step(AiSecurityAuditorAction(command="list_files"))
    print(f"Files: {result.observation.files}")

    # 3. Read a specific file
    result = env.step(AiSecurityAuditorAction(command="read_file", path="config.py"))
    print(f"Content:\n{result.observation.message}")

    # 4. Submit findings
    report = [
        VulnerabilityReport(
            file_path="config.py",
            vuln_type="Secret",
            line_number=4,
            severity="critical"
        )
    ]
    result = env.step(AiSecurityAuditorAction(command="submit_report", report=report))
    print(f"Score: {result.reward}")
```

---

## Environment Details

### Action Space (`AiSecurityAuditorAction`)
| Field | Type | Description |
|---|---|---|
| `command` | `Literal["list_files", "read_file", "submit_report"]` | The command to execute |
| `path` | `Optional[str]` | File path for `read_file` |
| `report` | `Optional[List[VulnerabilityReport]]` | Vulnerability list for `submit_report` |

### Observation Space (`AiSecurityAuditorObservation`)
| Field | Type | Description |
|---|---|---|
| `message` | `str` | Status messages or file contents |
| `files` | `Optional[List[str]]` | Directory listings from `list_files` |
| `success` | `bool` | `True` if submitted report scored > 0.8 |
| `error` | `Optional[str]` | Error message if an action failed |

---

## Task Descriptions

### Task 1 – Secret Detection (Easy)
- **File:** `config.py`
- **Vulnerability:** Hardcoded AWS Access Key ID and Secret Access Key stored in plaintext.
- **Goal:** Report lines 4 and 5 with `vuln_type="Secret"` and `severity="critical"`.

### Task 2 – SQL Injection (Medium)
- **File:** `app.py`
- **Vulnerability:** Raw user input concatenated directly into a SQL query string (`% username`).
- **Goal:** Report line 11 with `vuln_type="SQLi"` and `severity="high"`.

### Task 3 – Path Traversal (Hard)
- **File:** `utils.py`
- **Vulnerability:** Unsanitized `filename` parameter passed to `os.path.join()`, allowing `../../etc/passwd` traversal.
- **Goal:** Report line 7 with `vuln_type="Path Traversal"` and `severity="high"`.

---

## Graders

Each task uses a programmatic grader (`_grade_report`) that evaluates:
- **Precision:** How many of the reported vulnerabilities were correct.
- **Recall:** How many of the actual vulnerabilities were found.
- **F1-Score:** Harmonic mean of precision and recall (used as the reward signal, range `0.0–1.0`).

Matching criteria:
- `file_path` must match exactly.
- `vuln_type` must be a case-insensitive substring match.
- `line_number` must be within ±1 of the ground truth.

---

## Reward Function

| Action | Reward |
|---|---|
| Correct `submit_report` (full credit) | 1.0 (F1 = 1.0) |
| Partial findings | 0.0–1.0 (partial F1) |
| Empty report | 0.0 |
| Wrong file name in `read_file` | −0.1 |
| Unknown command | −0.1 |

---

## Baseline Performance

> Scores produced by running `inference.py` with `llama-3.3-70b-versatile` via Groq API.

| Task | Name | Baseline Score |
|---|---|---|
| task_1 | Secret Detection (Easy) | 1.0000 |
| task_2 | SQL Injection (Medium) | 1.0000 |
| task_3 | Path Traversal (Hard) | 1.0000 |

*Scores reflect perfect identification (F1=1.0) of target vulnerabilities.*

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- `uv` package manager (`pip install uv`)
- An OpenAI-compatible API key (set as `OPENAI_API_KEY`)

### 1. Install Dependencies
```bash
cd AI_SECURITY_AUDITOR
uv sync
```

### 2. Run the Server Locally
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### 3. Run Baseline Inference
```bash
# From the project root (one level above AI_SECURITY_AUDITOR/)
export OPENAI_API_KEY="your-key-here"
python inference.py
```

### 4. Build & Run with Docker
```bash
# Build from project root
docker build -t ai-security-auditor:latest .

# Run
docker run -p 7860:7860 -e OPENAI_API_KEY="your-key" ai-security-auditor:latest
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ Yes | Primary API key for LLM inference |
| `GROQ_API_KEY` | Optional | Fallback key for Groq API |
| `API_BASE_URL` | Optional | Base URL for LLM API (default: Groq) |
| `MODEL_NAME` | Optional | LLM model name (default: `llama-3.3-70b-versatile`) |
| `HF_TOKEN` | Optional | Hugging Face token for private Space access |

---

## Project Structure
```
AI SECURITY AUDITOR/          ← project root
├── openenv.yaml              # OpenEnv manifest (root-level copy)
├── inference.py              # Baseline LLM inference script
├── Dockerfile                # Container definition
├── .dockerignore
└── AI_SECURITY_AUDITOR/      # Environment package
    ├── openenv.yaml          # OpenEnv manifest
    ├── pyproject.toml        # Package configuration
    ├── models.py             # Pydantic models: Action / Observation
    ├── client.py             # Environment client implementation
    └── server/
        ├── AI_SECURITY_AUDITOR_environment.py  # Core auditing logic & grader
        └── app.py            # FastAPI server (HTTP + WebSocket endpoints)
```
