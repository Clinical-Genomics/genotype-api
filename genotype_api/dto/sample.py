"""Module for the sample DTOs."""

from datetime import datetime
from pydantic import BaseModel, field_validator
from genotype_api.constants import Sexes, Status, Types
from genotype_api.dto.genotype import GenotypeResponse

from genotype_api.models import SampleDetail
from genotype_api.services.match_genotype_service.utils import check_snps, check_sex


class AnalysisOnSample(BaseModel):
    type: Types | None = None
    sex: Sexes | None = None
    sample_id: str | None = None
    plate_id: int | None = None
    id: int | None = None
    genotypes: list[GenotypeResponse]


class SampleResponse(BaseModel):
    id: str | None = None
    status: Status | None = None
    comment: str | None = None
    sex: Sexes | None = None
    created_at: datetime | None = datetime.now()
    analyses: list[AnalysisOnSample] | None = None
    detail: SampleDetail | None = None

    @field_validator("detail")
    def get_detail(cls, value, values) -> SampleDetail | None:
        analyses = values.get("analyses")
        if analyses:
            if len(analyses) != 2:
                return SampleDetail()
            genotype_analysis: list[AnalysisOnSample] = [
                analysis for analysis in analyses if analysis.type == "genotype"
            ][0]
            sequence_analysis: list[AnalysisOnSample] = [
                analysis for analysis in analyses if analysis.type == "sequence"
            ][0]
            status: dict = check_snps(
                genotype_analysis=genotype_analysis, sequence_analysis=sequence_analysis
            )
            sex: str = check_sex(
                sample_sex=values.get("sex"),
                genotype_analysis=genotype_analysis,
                sequence_analysis=sequence_analysis,
            )

            return SampleDetail(**status, sex=sex)
        return None


class SampleCreate(BaseModel):
    id: str
    status: str | None = None
    comment: str | None = None
    sex: Sexes
    created_at: datetime = datetime.now()
