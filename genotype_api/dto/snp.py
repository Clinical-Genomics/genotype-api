"""Module to hold the SNP DTOs."""

from pydantic import BaseModel


class SNPResponse(BaseModel):
    ref: str | None = None
    chrom: str | None = None
    pos: int | None = None
    id: str | None = None
