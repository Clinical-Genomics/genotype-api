"""Module that holds the analysis dtos."""

from datetime import datetime

from pydantic import BaseModel

from genotype_api.constants import SEXES, TYPES
from genotype_api.dto.genotype import GenotypeBase


class AnalysisWithGenotypeResponse(BaseModel):
    type: TYPES | None
    source: str | None
    sex: SEXES | None
    created_at: datetime | None
    sample_id: str | None
    plate_id: str | None
    id: int | None
    genotypes: list[GenotypeBase] | None
