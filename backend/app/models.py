from typing import Literal, Any
from pydantic import BaseModel, Field

class Event(BaseModel):
    id: str
    at: str
    title: str
    detail: str = ""
    url: str | None = None

class Observation(BaseModel):
    version: Literal[1] = 1
    source_id: str
    instance_id: str = "synthetic-v1"
    health_notes: list[str] = Field(default_factory=list)
    origin: Literal['real', 'demo']
    source_observed_at: str | None = None
    heartbeat_at: str | None = None
    job_success_at: str | None = None
    provenance: str
    coverage: str
    data: dict[str, Any]
    events: list[Event] = Field(default_factory=list)
