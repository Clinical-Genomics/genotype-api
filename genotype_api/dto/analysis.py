"""Module that holds the analysis DTOs."""

from datetime import datetime

from pydantic import BaseModel

from genotype_api.constants import Sexes, Types
from genotype_api.dto.genotype import GenotypeResponse


class AnalysisResponse(BaseModel):
    type: Types | None = None
    source: str | None = None
    sex: Sexes | None = None
    created_at: datetime | None = None
    sample_id: str | None = None
    plate_id: str | None = None
    id: int | None = None
    genotypes: list[GenotypeResponse] | None = None
