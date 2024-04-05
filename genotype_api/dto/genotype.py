"""Module to hold the genotype DTOs."""

from pydantic import BaseModel, Field


class GenotypeResponse(BaseModel):
    rsnumber: str | None = Field(default=None, max_length=10)
    analysis_id: int | None = None
    allele_1: str | None = Field(default=None, max_length=1)
    allele_2: str | None = Field(default=None, max_length=1)

    @property
    def alleles(self):
        return sorted([self.allele_1, self.allele_2])
