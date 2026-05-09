from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ExpertOpinion(BaseModel):
    expert_role: str
    opinion: str


class ConsensusArtifact(BaseModel):
    summary: str
    opinions: List[ExpertOpinion] = Field(default_factory=list)


class ExpertPanelProtocol:
    def build_consensus(
        self,
        opinions: List[ExpertOpinion],
    ) -> ConsensusArtifact:
        summary = "\n".join(
            f"[{opinion.expert_role}] {opinion.opinion}"
            for opinion in opinions
        )

        return ConsensusArtifact(
            summary=summary,
            opinions=opinions,
        )
