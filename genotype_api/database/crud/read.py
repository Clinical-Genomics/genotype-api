import logging
from datetime import timedelta, date
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Query
from genotype_api.constants import Types
from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.filter_models.plate_models import PlateOrderParams
from genotype_api.database.filter_models.sample_models import SampleFilterParams
from genotype_api.database.filters.analysis_filter import apply_analysis_filter, AnalysisFilter
from genotype_api.database.filters.genotype_filters import apply_genotype_filter, GenotypeFilter
from genotype_api.database.filters.plate_filters import PlateFilter, apply_plate_filter
from genotype_api.database.filters.sample_filters import apply_sample_filter, SampleFilter
from genotype_api.database.filters.snp_filters import SNPFilter, apply_snp_filter
from genotype_api.database.filters.user_filters import apply_user_filter, UserFilter
from genotype_api.database.models import (
    Analysis,
    Plate,
    Sample,
    User,
    SNP,
    Genotype,
)

LOG = logging.getLogger(__name__)


class ReadHandler(BaseHandler):

    def get_analyses_by_plate_id(self, plate_id: int) -> list[Analysis]:
        analyses: Query = self._get_query(Analysis)
        filter_functions = [AnalysisFilter.BY_PLATE_ID]
        return apply_analysis_filter(
            analyses=analyses, filter_functions=filter_functions, plate_id=plate_id
        ).all()

    def get_analysis_by_id(self, analysis_id: int) -> Analysis:
        analyses: Query = self._get_query(Analysis)
        filter_functions = [AnalysisFilter.BY_ID]
        return apply_analysis_filter(
            analyses=analyses, filter_functions=filter_functions, analysis_id=analysis_id
        ).first()

    def get_analyses(self) -> list[Analysis]:
        return self._get_query(Analysis).all()

    def get_analyses_with_skip_and_limit(self, skip: int, limit: int) -> list[Analysis]:
        analyses: Query = self._get_query(Analysis)
        filter_functions = [AnalysisFilter.SKIP_AND_LIMIT]
        return apply_analysis_filter(
            analyses=analyses, filter_functions=filter_functions, skip=skip, limit=limit
        ).all()

    def get_analyses_by_type_between_dates(
        self, analysis_type: Types, date_min: date, date_max: date
    ) -> list[Analysis]:
        analyses: Query = self._get_query(Analysis)
        filter_functions = [AnalysisFilter.BY_TYPE_BETWEEN_DATES]
        return apply_analysis_filter(
            analyses=analyses,
            filter_functions=filter_functions,
            date_min=date_min,
            date_max=date_max,
            type=analysis_type,
        ).all()

    def get_analysis_by_type_and_sample_id(self, analysis_type: str, sample_id: str) -> Analysis:
        analyses: Query = self._get_query(Analysis)
        filter_functions = [AnalysisFilter.BY_TYPE, AnalysisFilter.BY_SAMPLE_ID]
        return apply_analysis_filter(
            analyses=analyses,
            filter_functions=filter_functions,
            sample_id=sample_id,
            type=analysis_type,
        ).first()

    def get_plate_by_id(self, plate_id: int) -> Plate:
        plates: Query = self._get_query(Plate)
        filter_functions = [PlateFilter.BY_ID]
        return apply_plate_filter(
            plates=plates, filter_functions=filter_functions, entry_id=plate_id
        ).first()

    def get_plate_by_plate_id(self, plate_id: str) -> Plate:
        plates: Query = self._get_query(Plate)
        filter_functions = [PlateFilter.BY_PLATE_ID]
        return apply_plate_filter(
            plates=plates, filter_functions=filter_functions, plate_id=plate_id
        ).first()

    def get_ordered_plates(self, order_params: PlateOrderParams) -> list[Plate]:
        sort_func = desc if order_params.sort_order == "descend" else asc
        plates: Query = self._get_query(Plate)
        filter_functions = [PlateFilter.ORDER, PlateFilter.SKIP_AND_LIMIT]
        return apply_plate_filter(
            plates=plates,
            filter_functions=filter_functions,
            order_by=order_params.order_by,
            skip=order_params.skip,
            limit=order_params.limit,
            sort_func=sort_func,
        ).all()

    def get_genotype_by_id(self, entry_id: int) -> Genotype:
        genotypes: Query = self._get_query(Genotype)
        filter_functions = [GenotypeFilter.BY_ID]
        return apply_genotype_filter(
            genotypes=genotypes, filter_functions=filter_functions, entry_id=entry_id
        ).first()

    def get_filtered_samples(self, filter_params: SampleFilterParams) -> list[Sample]:
        samples = self._get_join_analysis_on_sample()
        return self._get_filtered_samples(samples=samples, filter_params=filter_params).all()

    @staticmethod
    def _get_filtered_samples(samples: Query, filter_params: SampleFilterParams) -> Query:
        filter_functions = [
            SampleFilter.CONTAINS_ID,
            SampleFilter.BY_PLATE_ID,
            SampleFilter.INCOMPLETE,
            SampleFilter.COMMENTED,
            SampleFilter.STATUS_MISSING,
            SampleFilter.SKIP_AND_LIMIT,
        ]
        return apply_sample_filter(
            samples=samples,
            filter_functions=filter_functions,
            sample_id=filter_params.sample_id,
            plate_id=filter_params.plate_id,
            is_incomplete=filter_params.is_incomplete,
            is_commented=filter_params.is_commented,
            is_missing=filter_params.is_missing,
            skip=filter_params.skip,
            limit=filter_params.limit,
        )
        return samples

    def get_sample_by_id(self, sample_id: str) -> Sample:
        samples: Query = self._get_query(Sample)
        filter_functions = [SampleFilter.BY_ID]
        return apply_sample_filter(
            samples=samples, filter_functions=filter_functions, sample_id=sample_id
        ).first()

    def get_user_by_id(self, user_id: int) -> User:
        users: Query = self._get_query(User)
        filter_functions = [UserFilter.BY_ID]
        return apply_user_filter(
            users=users, filter_functions=filter_functions, user_id=user_id
        ).first()

    def get_user_by_email(self, email: str) -> User | None:
        users: Query = self._get_query(User)
        filter_functions = [UserFilter.BY_EMAIL]
        return apply_user_filter(
            users=users, filter_functions=filter_functions, email=email
        ).first()

    def get_users_with_skip_and_limit(self, skip: int, limit: int) -> list[User]:
        users: Query = self._get_query(User)
        filter_functions = [UserFilter.SKIP_AND_LIMIT]
        return apply_user_filter(
            users=users, filter_functions=filter_functions, skip=skip, limit=limit
        ).all()

    def check_analyses_objects(self, analyses: list[Analysis], analysis_type: Types) -> None:
        """Raising 400 if any analysis in the list already exist in the database"""
        for analysis_obj in analyses:
            existing_analysis = self.get_analysis_by_type_and_sample_id(
                sample_id=analysis_obj.sample_id,
                analysis_type=analysis_type,
            )
            if existing_analysis:
                self.session.delete(existing_analysis)

    def get_snps(self) -> list[SNP]:
        return self._get_query(SNP).all()

    def get_snps_by_limit_and_skip(self, skip: int, limit: int) -> list[SNP]:
        snps: Query = self._get_query(SNP)
        filter_functions = [SNPFilter.SKIP_AND_LIMIT]
        return apply_snp_filter(
            snps=snps, filter_functions=filter_functions, skip=skip, limit=limit
        ).all()
