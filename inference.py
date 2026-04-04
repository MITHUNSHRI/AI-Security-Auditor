import os
import json
from openai import OpenAI
from client import AiSecurityAuditorEnv
from models import AiSecurityAuditorAction, VulnerabilityReport

# ── Configuration ──────────────────────────────────────────────────────────────
# OPENAI_API_KEY is the required primary key per OpenEnv spec.
# GROQ_API_KEY is accepted as a fallback for local development.
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "llama-3.3-70b-versatile")
API_KEY      = os.environ.get("OPENAI_API_KEY", os.environ.get("GROQ_API_KEY"))

if not API_KEY:
    raise EnvironmentError(
        "No API key found. Set OPENAI_API_KEY (or GROQ_API_KEY) before running."
    )

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are an automated security auditor agent. Analyze code files and find vulnerabilities.

You must respond with ONLY a single JSON object — no markdown, no explanation.

Available commands and their JSON format:

1. List files in the environment:
   {"command": "list_files"}

2. Read a specific file (use the exact filename from list_files):
   {"command": "read_file", "path": "filename.py"}

3. Submit your vulnerability report when done (REQUIRED to finish the task):
   {"command": "submit_report", "report": [
     {"file_path": "filename.py", "vuln_type": "Secret|SQLi|Path Traversal", "line_number": 4, "severity": "low|medium|high|critical"}
   ]}

Strategy:
- Step 1: Call list_files to see available files.
- Step 2: Call read_file for each file listed.
- Step 3: Identify vulnerabilities from the code.
- Step 4: Call submit_report with ALL findings. Do NOT keep calling list_files.

You MUST call submit_report before step 8. Failure to submit = score of 0.
"""


def parse_model_action(response_text: str) -> AiSecurityAuditorAction:
    """Parses the model response into an AiSecurityAuditorAction."""
    text = response_text.strip()

    # Strip markdown code fences if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    # Find the first {...} block in the response
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]

    try:
        data = json.loads(text)
        # Reconstruct report as VulnerabilityReport objects if present
        if "report" in data and isinstance(data["report"], list):
            data["report"] = [VulnerabilityReport(**v) for v in data["report"]]
        return AiSecurityAuditorAction(**data)
    except Exception as e:
        print(f"  [WARN] Failed to parse model response: {e!r}")
        print(f"  [WARN] Raw response: {response_text[:200]!r}")
        # Safe fallback: list files
        return AiSecurityAuditorAction(command="list_files")


def run_task(task_id: str) -> float:
    """Run a single task and return the final score."""
    print(f"[START] task_id={task_id}")

    score = 0.0
    try:
        with AiSecurityAuditorEnv(base_url="http://localhost:7860").sync() as env:
            result = env.reset(task_id=task_id)
            print(f"[STEP] step=0 phase=reset observation={result.observation.message!r}")

            history = []
            max_steps = 10

            for step in range(1, max_steps + 1):
                # ── Build context for the model ───────────────────────────
                context_lines = [f"Step {step}/{max_steps}."]
                context_lines.append(f"Last observation: {result.observation.message}")
                if result.observation.files:
                    context_lines.append(f"Files available: {', '.join(result.observation.files)}")
                if history:
                    context_lines.append("History (last 5 steps):")
                    for h in history[-5:]:
                        context_lines.append(f"  - {h}")
                context_lines.append(
                    "IMPORTANT: If you have read all files, you MUST now call submit_report. "
                    "Do NOT keep calling list_files."
                )
                user_content = "\n".join(context_lines)

                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_content},
                ]

                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=0.0,
                )

                response_text = completion.choices[0].message.content
                action = parse_model_action(response_text)

                print(
                    f"[STEP] step={step} action={action.command}"
                    + (f" path={action.path!r}" if action.path else "")
                    + (f" report_count={len(action.report)}" if action.report else "")
                )

                result = env.step(action)

                history.append(
                    f"step={step} cmd={action.command}"
                    + (f" path={action.path}" if action.path else "")
                    + f" → {result.observation.message}"
                    + (f" | files={result.observation.files}" if result.observation.files else "")
                )

                if result.done:
                    score = result.reward if result.reward is not None else 0.0
                    print(f"[STEP] step={step} phase=done score={score:.4f}")
                    break
            else:
                print(f"[STEP] phase=timeout reason=max_steps_reached score={score:.4f}")

    except Exception as e:
        print(f"[STEP] phase=error reason={e!r}")

    print(f"[END] task_id={task_id} score={score:.4f}")
    return score


if __name__ == "__main__":
    task_ids = ["task_1", "task_2", "task_3"]
    total_score = 0.0
    results = {}

    for task_id in task_ids:
        s = run_task(task_id)
        results[task_id] = s
        total_score += s
        print()

    avg = total_score / len(task_ids)
    print("=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    for tid, sc in results.items():
        print(f"  {tid}: {sc:.4f}")
    print(f"  Average: {avg:.4f}")
    print("=" * 50)
