"""Module to hold the genotype DTOs."""

from pydantic import BaseModel, Field


class GenotypeBase(BaseModel):
    rsnumber: str = Field(max_length=10)
    analysis_id: int
    allele_1: str = Field(max_length=1)
    allele_2: str = Field(max_length=1)
