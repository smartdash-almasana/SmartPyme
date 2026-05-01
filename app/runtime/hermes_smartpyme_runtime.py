from __future__ import annotations

import os
import sys
from pathlib import Path


class HermesSmartPymeRuntime:
    DEFAULT_HERMES_REPO_PATH = Path("/data/repos/hermes-agent")

    def __init__(self, hermes_repo_path: str | Path) -> None:
        self.hermes_repo_path = Path(hermes_repo_path)

    @classmethod
    def from_env(cls) -> HermesSmartPymeRuntime:
        hermes_repo_path = os.environ.get("HERMES_REPO_PATH")
        return cls(hermes_repo_path or cls.DEFAULT_HERMES_REPO_PATH)

    def load_ai_agent_class(self) -> type:
        if not self.hermes_repo_path.exists():
            raise FileNotFoundError(
                f"Hermes repo path not available: {self.hermes_repo_path}"
            )

        hermes_path = str(self.hermes_repo_path)
        if sys.path[:1] != [hermes_path]:
            if hermes_path in sys.path:
                sys.path.remove(hermes_path)
            sys.path.insert(0, hermes_path)

        from run_agent import AIAgent

        return AIAgent
