"""Module to hold the SNP DTOs."""

from pydantic import BaseModel


class SNPResponse(BaseModel):
    ref: str
    chrom: str
    pos: int | None
    id: str
