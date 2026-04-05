# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
FastAPI application for the Ai Security Auditor Environment.

This module creates an HTTP server that exposes the AiSecurityAuditorEnvironment
over HTTP and WebSocket endpoints, compatible with EnvClient.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas
    - WS /ws: WebSocket endpoint for persistent sessions

Usage:
    # Development (with auto-reload):
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4

    # Or run directly:
    python -m server.app
"""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e

try:
    from ..models import AiSecurityAuditorAction, AiSecurityAuditorObservation
    from .AI_SECURITY_AUDITOR_environment import AiSecurityAuditorEnvironment
except (ModuleNotFoundError, ImportError):
    from models import AiSecurityAuditorAction, AiSecurityAuditorObservation
    from server.AI_SECURITY_AUDITOR_environment import AiSecurityAuditorEnvironment


from fastapi.responses import HTMLResponse

# Create the app with web interface and README integration
app = create_app(
    AiSecurityAuditorEnvironment,
    AiSecurityAuditorAction,
    AiSecurityAuditorObservation,
    env_name="AI_SECURITY_AUDITOR",
    max_concurrent_envs=1,
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Security Auditor Env</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            :root { --primary: #ff4d4d; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }
            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .container { background: var(--card); padding: 3rem; border-radius: 1.5rem; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); max-width: 600px; width: 90%; border: 1px solid rgba(255,255,255,0.1); }
            h1 { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; background: linear-gradient(to right, #ff4d4d, #f97316); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            p { color: #94a3b8; line-height: 1.6; font-size: 1.1rem; }
            .status { display: inline-flex; align-items: center; background: rgba(34, 197, 94, 0.2); color: #4ade80; padding: 0.5rem 1rem; border-radius: 2rem; font-size: 0.875rem; font-weight: 600; margin-bottom: 2rem; }
            .status::before { content: ''; width: 8px; height: 8px; background: #4ade80; border-radius: 50%; margin-right: 8px; box-shadow: 0 0 10px #4ade80; }
            .tasks { display: grid; gap: 1rem; margin: 2rem 0; }
            .task { background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 0.75rem; border-left: 4px solid var(--primary); }
            .btn { display: inline-block; background: var(--primary); color: white; padding: 1rem 2rem; border-radius: 0.75rem; text-decoration: none; font-weight: 600; transition: transform 0.2s, background 0.2s; text-align: center; width: 100%; box-sizing: border-box; }
            .btn:hover { transform: translateY(-2px); background: #ef4444; }
            .secondary { color: #94a3b8; display: block; text-align: center; margin-top: 1.5rem; text-decoration: none; font-size: 0.9rem; }
            .secondary:hover { color: #f8fafc; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status">ENVIRONMENT ACTIVE</div>
            <h1>AI Security Auditor</h1>
            <p>Welcome to the OpenEnv Cybersecurity Training Ground. This sandbox is designed for AI agents to autonomously identify vulnerabilities.</p>
            
            <div class="tasks">
                <div class="task"><strong>Easy:</strong> Secret Key Detection</div>
                <div class="task"><strong>Medium:</strong> SQL Injection Audit</div>
                <div class="task"><strong>Hard:</strong> Path Traversal Logic</div>
            </div>

            <a href="/docs" class="btn">View API Documentation</a>
            <a href="https://huggingface.co/spaces/mithunshri2005/ai-security-auditor-env/tree/main" target="_blank" class="secondary">View Source Code on Hugging Face</a>
        </div>
    </body>
    </html>
    """



def main():
    """
    Run the FastAPI server.
    """
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
