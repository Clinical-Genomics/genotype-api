"""Module for the sample DTOs."""

from datetime import datetime
from pydantic import BaseModel, validator
from genotype_api.constants import Sexes, Status, Types

from genotype_api.models import SampleDetail
from genotype_api.services.match_genotype_service.utils import check_snps, check_sex


class AnalysisOnSample(BaseModel):
    type: Types | None = None
    sex: Sexes | None = None
    sample_id: str | None = None
    plate_id: str | None = None
    id: int | None = None


class SampleResponse(BaseModel):
    id: str | None = None
    status: Status | None
    comment: str | None
    sex: Sexes | None
    created_at: datetime | None = datetime.now()
    analyses: list[AnalysisOnSample]
    detail: SampleDetail | None

    @validator("detail")
    def get_detail(cls, value, values) -> SampleDetail | None:
        analyses = values.get("analyses")
        if analyses:
            if len(analyses) != 2:
                return SampleDetail()
            genotype_analysis = [analysis for analysis in analyses if analysis.type == "genotype"][
                0
            ]
            sequence_analysis = [analysis for analysis in analyses if analysis.type == "sequence"][
                0
            ]
            status = check_snps(
                genotype_analysis=genotype_analysis, sequence_analysis=sequence_analysis
            )
            sex = check_sex(
                sample_sex=values.get("sex"),
                genotype_analysis=genotype_analysis,
                sequence_analysis=sequence_analysis,
            )

            return SampleDetail(**status, sex=sex)
        return None
