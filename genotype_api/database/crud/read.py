import logging
from datetime import date

from sqlalchemy import asc, desc, func
from sqlalchemy.future import select
from sqlalchemy.orm import Query, selectinload

from genotype_api.constants import Types
from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.filter_models.plate_models import PlateOrderParams
from genotype_api.database.filter_models.sample_models import SampleFilterParams
from genotype_api.database.filters.analysis_filter import (
    AnalysisFilter,
    apply_analysis_filter,
    filter_analyses_by_id,
    filter_analyses_by_plate_id,
)
from genotype_api.database.filters.genotype_filters import (
    GenotypeFilter,
    apply_genotype_filter,
)
from genotype_api.database.filters.plate_filters import (
    PlateFilter,
    apply_plate_filter,
    filter_plates_by_id,
    filter_plates_by_plate_id,
)
from genotype_api.database.filters.sample_filters import (
    SampleFilter,
    apply_sample_filter,
    filter_samples_by_id,
)
from genotype_api.database.filters.snp_filters import SNPFilter, apply_snp_filter
from genotype_api.database.filters.user_filters import (
    UserFilter,
    apply_user_filter,
    filter_users_by_email,
    filter_users_by_id,
)
from genotype_api.database.models import SNP, Analysis, Genotype, Plate, Sample, User

LOG = logging.getLogger(__name__)


class ReadHandler(BaseHandler):

    async def get_analyses_by_plate_id(self, plate_id: int) -> list[Analysis]:
        analyses: Query = self._get_analysis_with_genotypes()
        filtered_query = filter_analyses_by_plate_id(plate_id=plate_id, analyses=analyses)
        return await self.fetch_all_rows(filtered_query)

    async def get_analysis_by_id(self, analysis_id: int) -> Analysis:
        analyses: Query = select(Analysis)
        filtered_query = filter_analyses_by_id(analysis_id=analysis_id, analyses=analyses)
        return await self.fetch_first_row(filtered_query)

    async def get_analyses(self) -> list[Analysis]:
        filtered_query = select(Analysis)
        return await self.fetch_all_rows(filtered_query)

    async def get_analyses_with_skip_and_limit(self, skip: int, limit: int) -> list[Analysis]:
        analyses: Query = select(Analysis)
        filter_functions = [AnalysisFilter.SKIP_AND_LIMIT]
        filtered_query = apply_analysis_filter(
            analyses=analyses, filter_functions=filter_functions, skip=skip, limit=limit
        )
        return await self.fetch_all_rows(filtered_query)

    async def get_analyses_by_type_between_dates(
        self, analysis_type: Types, date_min: date, date_max: date
    ) -> list[Analysis]:
        analyses: Query = select(Analysis)
        filter_functions = [AnalysisFilter.BY_TYPE, AnalysisFilter.BETWEEN_DATES]
        filtered_query = apply_analysis_filter(
            analyses=analyses,
            filter_functions=filter_functions,
            date_min=date_min,
            date_max=date_max,
            type=analysis_type,
        )

        filtered_query = filtered_query.options(selectinload(Analysis.genotypes))
        return await self.fetch_all_rows(filtered_query)

    async def get_analysis_by_type_and_sample_id(
        self, sample_id: str, analysis_type: Types
    ) -> Analysis:
        analyses: Query = select(Analysis)
        filter_functions = [AnalysisFilter.BY_TYPE, AnalysisFilter.BY_SAMPLE_ID]
        filtered_query = apply_analysis_filter(
            analyses=analyses,
            filter_functions=filter_functions,
            sample_id=sample_id,
            type=analysis_type,
        )
        filtered_query = filtered_query.options(selectinload(Analysis.genotypes))
        return await self.fetch_first_row(filtered_query)

    async def get_plate_by_id(self, plate_id: int) -> Plate:
        plates: Query = self._get_plate_with_analyses_and_samples()
        filtered_query = filter_plates_by_id(entry_id=plate_id, plates=plates)
        return await self.fetch_first_row(filtered_query)

    async def get_plate_by_plate_id(self, plate_id: str) -> Plate:
        plates: Query = self._get_plate_with_analyses
        filtered_query = filter_plates_by_plate_id(plate_id=plate_id, plates=plates)
        return await self.fetch_first_row(filtered_query)

    async def get_ordered_plates(self, order_params: PlateOrderParams) -> list[Plate]:
        sort_func = desc if order_params.sort_order == "descend" else asc
        plates: Query = self._get_plate_with_analyses_and_samples()
        filter_functions = [PlateFilter.ORDER, PlateFilter.SKIP_AND_LIMIT]
        filtered_query = apply_plate_filter(
            plates=plates,
            filter_functions=filter_functions,
            order_by=order_params.order_by,
            skip=order_params.skip,
            limit=order_params.limit,
            sort_func=sort_func,
        )
        return await self.fetch_all_rows(filtered_query)

    async def get_genotype_by_id(self, entry_id: int) -> Genotype:
        genotypes: Query = self._get_genotype_with_analysis()
        filter_functions = [GenotypeFilter.BY_ID]
        filtered_query = apply_genotype_filter(
            genotypes=genotypes, filter_functions=filter_functions, entry_id=entry_id
        )
        return await self.fetch_first_row(filtered_query)

    async def get_filtered_samples(self, filter_params: SampleFilterParams) -> list[Sample]:
        query = self._get_samples_with_analyses_and_genotypes()
        if filter_params.sample_id:
            query = self._get_samples(query, filter_params.sample_id)
        if filter_params.plate_id:
            query = self._get_plate_samples(query, filter_params.plate_id)
        if filter_params.is_incomplete:
            query = self._get_incomplete_samples(query)
        if filter_params.is_commented:
            query = self._get_commented_samples(query)
        if filter_params.is_missing:
            query = self._get_status_missing_samples(query)
        filtered_query = (
            query.order_by(Sample.created_at.desc())
            .offset(filter_params.skip)
            .limit(filter_params.limit)
        )
        return await self.fetch_all_rows(filtered_query)

    # pylint: disable=E1102
    @staticmethod
    def _get_incomplete_samples(query: Query) -> Query:
        """Returning sample query statement for samples with less than two analyses."""
        return (
            query.group_by(Analysis.sample_id)
            .order_by(Analysis.created_at)
            .having(func.count(Analysis.sample_id) < 2)
        )

    @staticmethod
    def _get_plate_samples(query: Query, plate_id: str) -> Query:
        """Returning sample query statement for samples analysed on a specific plate."""
        return query.filter(Analysis.plate_id == plate_id)

    @staticmethod
    def _get_commented_samples(query: Query) -> Query:
        """Returning sample query statement for samples with no comment."""
        return query.filter(Sample.comment.is_not(None))

    @staticmethod
    def _get_status_missing_samples(query: Query) -> Query:
        """Returning sample query statement for samples with no comment."""
        return query.filter(Sample.status.is_(None))

    @staticmethod
    def _get_samples(query: Query, sample_id: str) -> Query:
        """Returns a query for samples containing the given sample_id."""
        return query.filter(Sample.id.contains(sample_id))

    async def get_sample_by_id(self, sample_id: str) -> Sample:
        samples: Query = self._get_samples_with_analyses_and_genotypes()
        filtered_query = filter_samples_by_id(sample_id=sample_id, samples=samples)
        return await self.fetch_first_row(filtered_query)

    async def get_user_by_id(self, user_id: int) -> User:
        users: Query = self._get_user_with_plates()
        filtered_query = filter_users_by_id(user_id=user_id, users=users)
        return await self.fetch_first_row(filtered_query)

    async def get_user_by_email(self, email: str) -> User | None:
        users: Query = select(User)
        filtered_query = filter_users_by_email(email=email, users=users)
        return await self.fetch_first_row(filtered_query)

    async def get_users_with_skip_and_limit(self, skip: int, limit: int) -> list[User]:
        users: Query = self._get_user_with_plates()
        filter_functions = [UserFilter.SKIP_AND_LIMIT]
        filtered_query = apply_user_filter(
            users=users, filter_functions=filter_functions, skip=skip, limit=limit
        )
        return await self.fetch_all_rows(filtered_query)

    async def check_analyses_objects(self, analyses: list[Analysis], analysis_type: Types) -> None:
        """Raising 400 if any analysis in the list already exist in the database"""
        for analysis_obj in analyses:
            existing_analysis = await self.get_analysis_by_type_and_sample_id(
                sample_id=analysis_obj.sample_id,
                analysis_type=analysis_type,
            )
            if existing_analysis:
                await self.session.delete(existing_analysis)
                await self.session.commit()

    async def get_snps(self) -> list[SNP]:
        filtered_query = select(SNP)
        return await self.fetch_all_rows(filtered_query)

    async def get_snps_by_limit_and_skip(self, skip: int, limit: int) -> list[SNP]:
        snps: Query = select(SNP)
        filter_functions = [SNPFilter.SKIP_AND_LIMIT]
        filtered_query = apply_snp_filter(
            snps=snps, filter_functions=filter_functions, skip=skip, limit=limit
        )
        return await self.fetch_all_rows(filtered_query)

    @staticmethod
    def _get_analysis_with_genotypes_and_sample() -> Query:
        return select(Analysis).options(
            selectinload(Analysis.genotypes),
            selectinload(Analysis.sample),
        )

    @staticmethod
    def _get_analysis_with_genotypes() -> Query:
        return select(Analysis).options(selectinload(Analysis.genotypes))

    @staticmethod
    def _get_plate_with_analyses() -> Query:
        return select(Plate).options(selectinload(Plate.analyses))

    @staticmethod
    def _get_plate_with_analyses_and_samples() -> Query:
        return select(Plate).options(selectinload(Plate.analyses).selectinload(Analysis.sample))

    @staticmethod
    def _get_genotype_with_analysis() -> Query:
        return select(Genotype).options(selectinload(Genotype.analysis))

    @staticmethod
    def _get_samples_with_analyses_and_genotypes() -> Query:
        return (
            select(Sample)
            .distinct()
            .options(selectinload(Sample.analyses).selectinload(Analysis.genotypes))
            .join(Analysis, Analysis.sample_id == Sample.id)
        )

    @staticmethod
    def _get_user_with_plates() -> Query:
        return select(User).options(selectinload(User.plates))
