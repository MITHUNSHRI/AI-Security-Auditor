---
title: Ai Security Auditor Environment Server
emoji: 🛡️
colorFrom: red
colorTo: black
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - security
  - cybersecurity
---

# Ai Security Auditor Environment

A real-world simulation environment where AI agents act as security researchers to identify vulnerabilities in a codebase. The environment provides a structured way for agents to explore files and submit vulnerability reports, which are then programmatically graded.

## Overview

The AI Security Auditor presents the agent with several tasks of increasing difficulty:
1. **Secret Detection (Easy)**: Identify hardcoded credentials in configuration files.
2. **SQL Injection (Medium)**: Find unsanitized user input used in database queries.
3. **Path Traversal (Hard)**: Discover insecure file handling that allows unauthorized access.

## Quick Start

The simplest way to use the environment is through the `AiSecurityAuditorEnv` class:

```python
from AI_SECURITY_AUDITOR import AiSecurityAuditorAction, AiSecurityAuditorEnv, VulnerabilityReport

with AiSecurityAuditorEnv(base_url="http://localhost:8000") as env:
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

## Environment Details

### Action Space (`AiSecurityAuditorAction`)
- `command` (Literal): `list_files`, `read_file`, or `submit_report`.
- `path` (Optional[str]): Used for file operations.
- `report` (Optional[List[VulnerabilityReport]]): Used for submission.

### Observation Space (`AiSecurityAuditorObservation`)
- `message` (str): Status messages or file contents.
- `files` (List[str]): Directory listings.
- `success` (bool): Indicates if the submitted report was accurate.
- `reward` (float): F1-score of the audit findings (0.0 to 1.0).

### Graders
Each task includes a programmatic grader that evaluates:
- **Precision**: How many of the reported vulnerabilities were correct.
- **Recall**: How many of the actual vulnerabilities were found.
- **F1-Score**: The harmonic mean, used as the primary reward signal.

## Building and Running

### Build the Docker Image
```bash
docker build -t AI_SECURITY_AUDITOR-env:latest -f server/Dockerfile .
```

### Run Locally
```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Run Baseline Inference
```bash
export OPENAI_API_KEY="your-key"
python inference.py
```

## Project Structure
```
AI_SECURITY_AUDITOR/
├── openenv.yaml           # OpenEnv manifest with task definitions
├── models.py              # Pydantic models for Actions/Observations
├── client.py              # Environment client implementation
├── inference.py           # Baseline LLM inference script
└── server/
    ├── AI_SECURITY_AUDITOR_environment.py  # Core auditing logic
    ├── app.py             # FastAPI server
    └── Dockerfile         # Container definition
```
n (HTTP + WebSocket endpoints)
    └── Dockerfile         # Container image definition
```
