"""Module that holds the analysis dtos."""

from datetime import datetime

from pydantic import BaseModel

from genotype_api.constants import SEXES, TYPES
from genotype_api.dto.genotype import GenotypeBase


class AnalysisWithGenotypeResponse(BaseModel):
    type: TYPES
    source: str
    sex: SEXES
    created_at: datetime
    sample_id: str
    plate_id: str
    id: int
    genotypes: list[GenotypeBase]
