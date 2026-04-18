from dataclasses import dataclass
from typing import Literal
from uuid import uuid4

JobStatus = Literal["created", "completed"]


@dataclass
class Job:
    id: str
    status: JobStatus

    @classmethod
    def create(cls) -> "Job":
        return cls(id=str(uuid4()), status="created")
