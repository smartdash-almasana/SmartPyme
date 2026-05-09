from __future__ import annotations

from typing import Dict, List

from factory_v3.contracts.entities import AgentCard, AgentRole


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentCard] = {}

    def register(self, agent: AgentCard) -> None:
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> AgentCard | None:
        return self._agents.get(agent_id)

    def list_agents(self) -> List[AgentCard]:
        return list(self._agents.values())

    def find_by_role(self, role: AgentRole) -> List[AgentCard]:
        return [agent for agent in self._agents.values() if agent.role == role]

    def find_by_capability(self, capability: str) -> List[AgentCard]:
        return [agent for agent in self._agents.values() if capability in agent.capabilities]
