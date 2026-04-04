import os
import json
from typing import List
from openai import OpenAI
from AI_SECURITY_AUDITOR import AiSecurityAuditorEnv, AiSecurityAuditorAction

# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama-3.3-70b-versatile")
API_KEY = os.environ.get("GROQ_API_KEY", os.environ.get("OPENAI_API_KEY"))

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = """You are a Security Auditor. Your task is to find vulnerabilities in the provided codebase.
Available commands:
1. list_files(path: str)
2. read_file(path: str)
3. submit_report(report: List[Vulnerability])

Vulnerability format: {"file_path": str, "vuln_type": str, "line_number": int, "severity": str}

Analyze the files and submit a report when you are confident. Respond only with the command you want to run in JSON format."""

def parse_model_action(response_text: str) -> AiSecurityAuditorAction:
    """Parses the model response into an AiSecurityAuditorAction."""
    try:
        # Simple extraction logic for JSON in markdown blocks or raw text
        if "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        else:
            json_text = response_text.strip()
        
        data = json.loads(json_text)
        return AiSecurityAuditorAction(**data)
    except Exception as e:
        print(f"Error parsing model response: {e}")
        # Default fallback: list files in root
        return AiSecurityAuditorAction(command="list_files", path=".")

def run_task(task_id: str):
    print(f"\n--- Running Task: {task_id} ---")
    
    # In a real OpenEnv deployment, we'd connect to the server. 
    # For baseline testing, we'll assume the server is running on localhost:8000
    try:
        with AiSecurityAuditorEnv(base_url="http://localhost:8000").sync() as env:
            result = env.reset(task_id=task_id)
            print(f"Initial Observation: {result.observation.message}")
            
            history = []
            max_steps = 10
            
            for step in range(max_steps):
                # Prompt the model
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Step {step}. Last observation: {result.observation.message}. History: {history}"}
                ]
                
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=0.0
                )
                
                response_text = completion.choices[0].message.content
                action = parse_model_action(response_text)
                
                print(f"Step {step}: Action -> {action.command} {action.path or ''}")
                
                result = env.step(action)
                history.append(f"Action: {action.command}, Result: {result.observation.message}")
                
                if result.done:
                    print(f"Task Complete! Reward: {result.reward}")
                    break
            else:
                print("Reached maximum steps.")
    except Exception as e:
        print(f"Connection error: {e}. Make sure the server is running at http://localhost:8000")

if __name__ == "__main__":
    # In Round 1, the validator will run this script.
    # It should ideally loop through all tasks defined in openenv.yaml
    for task_id in ["task_1", "task_2", "task_3"]:
        run_task(task_id)
