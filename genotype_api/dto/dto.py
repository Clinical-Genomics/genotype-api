from collections import Counter

from pydantic import constr, validator

import genotype_api.database.models
from genotype_api.database import models
from genotype_api.models import SampleDetail
from genotype_api.dto.plate import PlateStatusCounts
from genotype_api.services.match_genotype_service.utils import check_snps, check_sex


class GenotypeRead(models.GenotypeBase):
    id: int


class GenotypeCreate(models.GenotypeBase):
    pass


class AnalysisRead(models.AnalysisBase):
    id: int


class AnalysisCreate(models.AnalysisBase):
    pass


class SampleRead(genotype_api.database.models.SampleBase):
    id: constr(max_length=32)


class SampleCreate(genotype_api.database.models.SampleBase):
    pass


class SNPRead(models.SNPBase):
    id: constr(max_length=32)


class UserRead(models.UserBase):
    id: int


class UserCreate(models.UserBase):
    pass


class PlateRead(models.PlateBase):
    id: str
    user: UserRead | None


class PlateCreate(models.PlateBase):
    analyses: list[models.Analysis] | None = []


class UserReadWithPlates(UserRead):
    plates: list[models.Plate] | None = []


class SampleReadWithAnalysis(SampleRead):
    analyses: list[AnalysisRead] | None = []


class AnalysisReadWithGenotype(AnalysisRead):
    genotypes: list[models.Genotype] | None = []


class SampleReadWithAnalysisDeep(SampleRead):
    analyses: list[AnalysisReadWithGenotype] | None = []
    detail: SampleDetail | None

    @validator("detail")
    def get_detail(cls, value, values) -> SampleDetail:
        analyses = values.get("analyses")
        if len(analyses) != 2:
            return SampleDetail()
        genotype_analysis = [analysis for analysis in analyses if analysis.type == "genotype"][0]
        sequence_analysis = [analysis for analysis in analyses if analysis.type == "sequence"][0]
        status = check_snps(
            genotype_analysis=genotype_analysis, sequence_analysis=sequence_analysis
        )
        sex = check_sex(
            sample_sex=values.get("sex"),
            genotype_analysis=genotype_analysis,
            sequence_analysis=sequence_analysis,
        )

        return SampleDetail(**status, sex=sex)

    class Config:
        validate_all = True


class AnalysisReadWithSample(AnalysisRead):
    sample: models.SampleSlim | None


class AnalysisReadWithSampleDeep(AnalysisRead):
    sample: SampleReadWithAnalysisDeep | None


class PlateReadWithAnalyses(PlateRead):
    analyses: list[AnalysisReadWithSample] | None = []


class PlateReadWithAnalysisDetail(PlateRead):
    analyses: list[AnalysisReadWithSample] | None = []
    detail: PlateStatusCounts | None

    @validator("detail")
    def check_detail(cls, value, values):
        analyses = values.get("analyses")
        statuses = [str(analysis.sample.status) for analysis in analyses]
        commented = sum(1 for analysis in analyses if analysis.sample.comment)
        status_counts = Counter(statuses)
        return PlateStatusCounts(**status_counts, total=len(analyses), commented=commented)

    class Config:
        validate_all = True


class PlateReadWithAnalysisDetailSingle(PlateRead):
    analyses: list[AnalysisReadWithSample] | None = []
    detail: PlateStatusCounts | None

    @validator("detail")
    def check_detail(cls, value, values):
        analyses = values.get("analyses")
        statuses = [str(analysis.sample.status) for analysis in analyses]
        commented = sum(1 for analysis in analyses if analysis.sample.comment)
        status_counts = Counter(statuses)
        return PlateStatusCounts(**status_counts, total=len(analyses), commented=commented)

    class Config:
        validate_all = True
