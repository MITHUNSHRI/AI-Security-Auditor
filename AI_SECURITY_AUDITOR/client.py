# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Ai Security Auditor Environment Client."""

from typing import Dict, Any

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import AiSecurityAuditorAction, AiSecurityAuditorObservation


class AiSecurityAuditorEnv(
    EnvClient[AiSecurityAuditorAction, AiSecurityAuditorObservation, State]
):
    """
    Client for the Ai Security Auditor Environment.
    """

    def _step_payload(self, action: AiSecurityAuditorAction) -> Dict:
        """Convert action to JSON payload."""
        return action.model_dump(exclude_none=True)

    def _parse_result(self, payload: Dict) -> StepResult[AiSecurityAuditorObservation]:
        """Parse server response into StepResult."""
        obs_data = payload.get("observation", {})
        observation = AiSecurityAuditorObservation(
            message=obs_data.get("message", ""),
            files=obs_data.get("files"),
            success=obs_data.get("success", False),
            error=obs_data.get("error"),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """Parse server response into State object."""
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
