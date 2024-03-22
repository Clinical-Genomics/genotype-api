"""Module for the sample DTOs."""

from pydantic import BaseModel

from genotype_api.constants import Status


class SampleStatusResponse(BaseModel):
    status: Status | None = None
    comment: str | None = None
