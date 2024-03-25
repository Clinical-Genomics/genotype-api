"""Module that holds the analysis DTOs."""

from datetime import datetime

from pydantic import BaseModel

from genotype_api.constants import Sexes, Types
from genotype_api.dto.genotype import GenotypeResponse
from genotype_api.dto.sample import SampleStatusResponse


class AnalysisResponse(BaseModel):
    type: Types | None
    source: str | None
    sex: Sexes | None
    created_at: datetime | None
    sample_id: str | None
    plate_id: str | None
    id: int | None
    genotypes: list[GenotypeResponse] | None = None


class AnalysisSampleResponse(BaseModel):
    type: Types | None
    source: str | None
    sex: Sexes | None
    created_at: datetime | None
    sample_id: str | None
    plate_id: str | None
    id: int | None
    sample: SampleStatusResponse | None = None
