# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Ai Security Auditor Environment.

The AI_SECURITY_AUDITOR environment simulates a security researcher auditing code.
"""

from typing import List, Optional, Literal
from openenv.core.env_server.types import Action, Observation
from pydantic import Field, BaseModel


class VulnerabilityReport(BaseModel):
    """A single vulnerability finding."""
    file_path: str = Field(..., description="Path to the vulnerable file")
    vuln_type: str = Field(..., description="Type of vulnerability (e.g., SQLi, Secret)")
    line_number: int = Field(..., description="Line number where the vulnerability starts")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Severity level")


class AiSecurityAuditorAction(Action):
    """Action for the Ai Security Auditor environment."""
    
    command: Literal["list_files", "read_file", "submit_report"] = Field(
        ..., description="The command to execute: list_files, read_file, or submit_report"
    )
    path: Optional[str] = Field(None, description="Path for list_files or read_file")
    report: Optional[List[VulnerabilityReport]] = Field(
        None, description="List of vulnerabilities for submit_report"
    )


class AiSecurityAuditorObservation(Observation):
    """Observation from the Ai Security Auditor environment."""

    message: str = Field(default="", description="Status message or file content")
    files: Optional[List[str]] = Field(None, description="List of files in directory")
    success: bool = Field(default=False, description="Whether the task was completed successfully")
    error: Optional[str] = Field(None, description="Error message if action failed")
