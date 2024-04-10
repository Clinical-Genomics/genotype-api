"""Module for the sample service."""

from datetime import date
from typing import Literal
from genotype_api.constants import Types, Sexes
from genotype_api.database.filter_models.sample_models import SampleFilterParams, SampleSexesUpdate
from genotype_api.database.models import Sample, Analysis

from genotype_api.dto.genotype import GenotypeResponse
from genotype_api.dto.sample import AnalysisOnSample, SampleResponse, SampleCreate
from genotype_api.exceptions import SampleNotFoundError
from genotype_api.models import SampleDetail, MatchResult
from genotype_api.services.endpoint_services.base_service import BaseService
from genotype_api.services.match_genotype_service.match_genotype import MatchGenotypeService


class SampleService(BaseService):

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
                allele_2=genotype_on_analysis.allele_2,
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
        sample: Sample = self.store.get_sample_by_id(sample_id=sample_id)
        if not sample:
            raise SampleNotFoundError
        if len(sample.analyses) == 2 and not sample.status:
            sample: Sample = self.store.refresh_sample_status(sample=sample)
        return self._get_sample_response(sample)

    def get_samples(self, filter_params: SampleFilterParams) -> list[SampleResponse]:
        samples: list[Sample] = self.store.get_filtered_samples(filter_params=filter_params)
        return [self._get_sample_response(sample) for sample in samples]

    def create_sample(self, sample_create: SampleCreate) -> None:
        sample = Sample(
            id=sample_create.id,
            status=sample_create.status,
            comment=sample_create.comment,
            sex=sample_create.sex,
            created_at=sample_create.created_at,
        )
        self.store.create_sample(sample=sample)

    def delete_sample(self, sample_id: str) -> None:
        sample: Sample = self.store.get_sample_by_id(sample_id=sample_id)
        for analysis in sample.analyses:
            self.store.delete_analysis(analysis=analysis)
        self.store.delete_sample(sample=sample)

    def get_status_detail(self, sample_id: str) -> SampleDetail:
        sample: Sample = self.store.get_sample_by_id(sample_id=sample_id)
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
        """Get the match results for an analysis type and the comparison type in a given time frame."""
        analyses: list[Analysis] = self.store.get_analyses_by_type_between_dates(
            analysis_type=comparison_set, date_max=date_max, date_min=date_min
        )
        sample_analysis: Analysis = self.store.get_analysis_by_type_and_sample_id(
            analysis_type=analysis_type, sample_id=sample_id
        )
        matches: list[MatchResult] = MatchGenotypeService.get_matches(
            analyses=analyses, sample_analysis=sample_analysis
        )
        return matches

    def set_sample_status(
        self, sample_id: str, status: Literal["pass", "fail", "cancel"] | None
    ) -> SampleResponse:
        sample: Sample = self.store.update_sample_status(sample_id=sample_id, status=status)
        return self._get_sample_response(sample)

    def set_sample_comment(self, sample_id: str, comment: str) -> SampleResponse:
        sample: Sample = self.store.update_sample_comment(sample_id=sample_id, comment=comment)
        return self._get_sample_response(sample)

    def set_sex(self, sample_id: str, sex: Sexes, genotype_sex: Sexes, sequence_sex: Sexes) -> None:
        sexes_update = SampleSexesUpdate(
            sample_id=sample_id, sex=sex, genotype_sex=genotype_sex, sequence_sex=sequence_sex
        )
        self.store.update_sample_sex(sexes_update=sexes_update)
