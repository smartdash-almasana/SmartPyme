from __future__ import annotations

from typing import Dict

from factory_v3.contracts.entities import AgentCard


class RuntimeRouter:
    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}

    def register_agent(self, agent: AgentCard) -> None:
        self.agents[agent.agent_id] = agent

    def resolve_agent(self, agent_id: str) -> AgentCard | None:
        return self.agents.get(agent_id)
