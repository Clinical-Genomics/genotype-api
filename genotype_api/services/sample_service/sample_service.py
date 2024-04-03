"""Module for the sample service."""

from datetime import date
from typing import Literal

from sqlmodel import Session

from genotype_api.constants import Types, Sexes
from genotype_api.database.crud.create import create_sample
from genotype_api.database.crud.delete import delete_analysis, delete_sample
from genotype_api.database.crud.read import (
    get_sample,
    get_filtered_samples,
    get_analysis_by_type_and_sample_id,
    get_analyses_by_type_between_dates,
)
from genotype_api.database.crud.update import (
    refresh_sample_status,
    update_sample_status,
    update_sample_comment,
    update_sample_sex,
)
from genotype_api.database.filter_models.sample_models import SampleFilterParams, SampleSexesUpdate
from genotype_api.database.models import Sample, Analysis
from genotype_api.dto.genotype import GenotypeResponse
from genotype_api.dto.sample import AnalysisOnSample, SampleResponse
from genotype_api.exceptions import SampleNotFoundError
from genotype_api.models import SampleDetail, MatchResult
from genotype_api.services.match_genotype_service.match_genotype import MatchGenotypeService


class SampleService:

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _get_genotype_on_analysis(analysis: Analysis) -> list[GenotypeResponse] | None:
        genotypes: list[GenotypeResponse] = []
        if not analysis.genotypes:
            return None
        for genotype_on_analysis in analysis.genotypes:
            genotype = GenotypeResponse(
                rsnumber=genotype_on_analysis.rsnumber,
                analysis_id=genotype_on_analysis.analysis_id,
                allele_1=genotype_on_analysis.allele_1,
                allele_2=genotype_on_analysis.allele_1,
            )
            genotypes.append(genotype)
        return genotypes

    def _get_analyses_on_sample(self, sample: Sample) -> list[AnalysisOnSample] | None:
        analyses: list[AnalysisOnSample] = []
        if not sample.analyses:
            return None
        for analysis in sample.analyses:
            genotypes: list[GenotypeResponse] = self._get_genotype_on_analysis(analysis)
            analysis_on_sample = AnalysisOnSample(
                type=analysis.type,
                sex=analysis.sex,
                sample_id=analysis.sample_id,
                plate_id=analysis.plate_id,
                id=analysis.id,
                genotypes=genotypes,
            )
            analyses.append(analysis_on_sample)
        return analyses

    def _get_sample_response(self, sample: Sample) -> SampleResponse:
        analyses: list[AnalysisOnSample] = self._get_analyses_on_sample(sample=sample)
        return SampleResponse(
            id=sample.id,
            status=sample.status,
            comment=sample.comment,
            sex=sample.sex,
            created_at=sample.created_at,
            analyses=analyses,
        )

    def get_sample(self, sample_id: str) -> SampleResponse:
        sample: Sample = get_sample(session=self.session, sample_id=sample_id)
        if not sample:
            raise SampleNotFoundError
        if len(sample.analyses) == 2 and not sample.status:
            sample: Sample = refresh_sample_status(session=self.session, sample=sample)
        return self._get_sample_response(sample)

    def get_samples(self, filter_params: SampleFilterParams) -> list[SampleResponse]:
        samples: list[Sample] = get_filtered_samples(
            session=self.session, filter_params=filter_params
        )
        return [self._get_sample_response(sample) for sample in samples]

    def create_sample(self, sample: Sample):
        create_sample(session=self.session, sample=sample)

    def delete_sample(self, sample_id: str):
        sample: Sample = get_sample(session=self.session, sample_id=sample_id)
        for analysis in sample.analyses:
            delete_analysis(session=self.session, analysis=analysis)
        delete_sample(session=self.session, sample=sample)

    def get_status_detail(self, sample_id: str) -> SampleDetail:
        sample: Sample = get_sample(session=self.session, sample_id=sample_id)
        if len(sample.analyses) != 2:
            return SampleDetail()
        return MatchGenotypeService.check_sample(sample=sample)

    def get_match_results(
        self,
        sample_id: str,
        analysis_type: Types,
        comparison_set: Types,
        date_min: date,
        date_max: date,
    ) -> list[MatchResult]:
        analyses: list[Analysis] = get_analyses_by_type_between_dates(
            session=self.session, analysis_type=comparison_set, date_max=date_max, date_min=date_min
        )
        sample_analysis: Analysis = get_analysis_by_type_and_sample_id(
            session=self.session, analysis_type=analysis_type, sample_id=sample_id
        )
        matches: list[MatchResult] = MatchGenotypeService.get_matches(
            analyses=analyses, sample_analysis=sample_analysis
        )
        return matches

    def set_sample_status(
        self, sample_id: str, status: Literal["pass", "fail", "cancel"] | None
    ) -> SampleResponse:
        sample: Sample = update_sample_status(
            session=self.session, sample_id=sample_id, status=status
        )
        return self._get_sample_response(sample)

    def set_sample_comment(self, sample_id: str, comment: str) -> SampleResponse:
        sample: Sample = update_sample_comment(
            session=self.session, sample_id=sample_id, comment=comment
        )
        return self._get_sample_response(sample)

    def set_sex(self, sample_id: str, sex: Sexes, genotype_sex: Sexes, sequence_sex: Sexes):
        sexes_update = SampleSexesUpdate(
            sample_id=sample_id, sex=sex, genotype_sex=genotype_sex, sequence_sex=sequence_sex
        )
        update_sample_sex(session=self.session, sexes_update=sexes_update)
