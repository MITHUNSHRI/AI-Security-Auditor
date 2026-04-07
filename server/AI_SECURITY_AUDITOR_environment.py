# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Ai Security Auditor Environment Implementation.

This environment simulates a security researcher auditing source code for vulnerabilities.
"""

import json
from uuid import uuid4
from typing import Dict, List, Any

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import AiSecurityAuditorAction, AiSecurityAuditorObservation, VulnerabilityReport
except ImportError:
    from models import AiSecurityAuditorAction, AiSecurityAuditorObservation, VulnerabilityReport


class AiSecurityAuditorEnvironment(Environment):
    """
    A security auditing environment where an agent identifies vulnerabilities in code.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    TASKS = {
        "task_1": {
            "name": "Secret Detection",
            "description": "Find hardcoded secrets in the configuration file.",
            "files": {
                "config.py": "import os\n\nDEBUG = True\nAWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'\nAWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'\n"
            },
            "vulnerabilities": [
                {"file_path": "config.py", "vuln_type": "Secret", "line_number": 4, "severity": "critical"},
                {"file_path": "config.py", "vuln_type": "Secret", "line_number": 5, "severity": "critical"}
            ]
        },
        "task_2": {
            "name": "SQL Injection",
            "description": "Identify a SQL injection vulnerability in the application login logic.",
            "files": {
                "app.py": "from flask import Flask, request\nimport sqlite3\n\napp = Flask(__name__)\n\n@app.route('/login')\ndef login():\n    username = request.args.get('username')\n    db = sqlite3.connect('users.db')\n    # Vulnerable line follows\n    query = \"SELECT * FROM users WHERE username = '%s'\" % username\n    cursor = db.execute(query)\n    return str(cursor.fetchone())\n"
            },
            "vulnerabilities": [
                {"file_path": "app.py", "vuln_type": "SQLi", "line_number": 11, "severity": "high"}
            ]
        },
        "task_3": {
            "name": "Path Traversal",
            "description": "Find a path traversal vulnerability in the file serving utility.",
            "files": {
                "utils.py": "import os\nfrom flask import send_file\n\ndef serve_user_file(filename):\n    # Vulnerable to path traversal (../)\n    base_path = '/app/data/uploads/'\n    full_path = os.path.join(base_path, filename)\n    return send_file(full_path)\n"
            },
            "vulnerabilities": [
                {"file_path": "utils.py", "vuln_type": "Path Traversal", "line_number": 7, "severity": "high"}
            ]
        }
    }

    def __init__(self, task_id: str = "task_1"):
        """Initialize the AI_SECURITY_AUDITOR environment."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.task_id = task_id
        if self.task_id not in self.TASKS:
            self.task_id = "task_1"
        self.task = self.TASKS[self.task_id]
        self.done = False

    def _clamp_reward(self, reward: float) -> float:
        """Ensures reward is strictly between 0 and 1 per validator requirement."""
        # Mapping 0 -> 0.05 and 1 -> 0.95 to stay safely within (0, 1)
        if reward <= 0.0:
            return 0.05
        if reward >= 1.0:
            return 0.95
        return reward

    def reset(self) -> AiSecurityAuditorObservation:
        """Reset the environment to a clean state."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.done = False
        return AiSecurityAuditorObservation(
            message=f"Environment ready for task: {self.task['name']}. Use list_files and read_file to investigate.",
            done=False,
            reward=self._clamp_reward(0.0),
        )

    def step(self, action: AiSecurityAuditorAction) -> AiSecurityAuditorObservation:  # type: ignore[override]
        """Execute a step based on the provided action."""
        self._state.step_count += 1
        
        if self.done:
            return AiSecurityAuditorObservation(
                message="Episode already completed.",
                done=True,
                reward=self._clamp_reward(0.0)
            )

        if action.command == "list_files":
            files = list(self.task["files"].keys())
            return AiSecurityAuditorObservation(
                message=f"Found {len(files)} file(s): {', '.join(files)}. Use read_file to inspect each one.",
                files=files,
                done=False,
                reward=self._clamp_reward(0.0)
            )

        elif action.command == "read_file":
            path = action.path
            if path in self.task["files"]:
                return AiSecurityAuditorObservation(
                    message=self.task["files"][path],
                    done=False,
                    reward=self._clamp_reward(0.0)
                )
            else:
                return AiSecurityAuditorObservation(
                    message=f"Error: File {path} not found.",
                    error=f"File {path} not found.",
                    done=False,
                    reward=self._clamp_reward(0.0) # Changed from -0.1 to stay in (0, 1)
                )

        elif action.command == "submit_report":
            self.done = True
            if not action.report:
                return AiSecurityAuditorObservation(
                    message="Submitted empty report.",
                    success=False,
                    done=True,
                    reward=self._clamp_reward(0.0)
                )
            
            raw_score, feedback = self._grade_report(action.report)
            score = self._clamp_reward(raw_score)
            return AiSecurityAuditorObservation(
                message=f"Report submitted. Score: {score:.2f}. Feedback: {feedback}",
                success=score > 0.8,
                done=True,
                reward=score
            )

        return AiSecurityAuditorObservation(
            message="Invalid command.",
            error="Unknown action command.",
            done=False,
            reward=self._clamp_reward(0.0) # Changed from -0.1 to stay in (0, 1)
        )

    def _grade_report(self, report: List[VulnerabilityReport]) -> (float, str):
        """Grades the report against the ground truth."""
        ground_truth = self.task["vulnerabilities"]
        total_found = 0
        
        for rep in report:
            for gt in ground_truth:
                if (rep.file_path == gt["file_path"] and 
                    rep.vuln_type.lower() in gt["vuln_type"].lower() and 
                    abs(rep.line_number - gt["line_number"]) <= 1):
                    total_found += 1
                    break
        
        precision = total_found / len(report) if report else 0
        recall = total_found / len(ground_truth) if ground_truth else 0
        
        # F1 Score is a good balanced reward
        if precision + recall == 0:
            f1 = 0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
            
        return f1, f"Found {total_found} of {len(ground_truth)} vulnerabilities."

    @property
    def state(self) -> State:
        return self._state
