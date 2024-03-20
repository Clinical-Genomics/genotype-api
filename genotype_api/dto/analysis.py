"""Module that holds the analysis dtos."""

from datetime import datetime

from pydantic import BaseModel

from genotype_api.constants import Sexes, Types
from genotype_api.dto.genotype import GenotypeBase


class AnalysisResponse(BaseModel):
    type: Types | None
    source: str | None
    sex: Sexes | None
    created_at: datetime | None
    sample_id: str | None
    plate_id: str | None
    id: int | None


class AnalysisWithGenotypeResponse(BaseModel):
    type: Types | None
    source: str | None
    sex: Sexes | None
    created_at: datetime | None
    sample_id: str | None
    plate_id: str | None
    id: int | None
    genotypes: list[GenotypeBase] | None
