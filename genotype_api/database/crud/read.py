import logging
from datetime import timedelta, date
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Query
from genotype_api.constants import Types
from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.filter_models.plate_models import PlateOrderParams
from genotype_api.database.filter_models.sample_models import SampleFilterParams
from genotype_api.database.models import (
    Analysis,
    Plate,
    Sample,
    User,
    SNP,
)

LOG = logging.getLogger(__name__)


class ReadHandler(BaseHandler):

    def get_analyses_from_plate(self, plate_id: int) -> list[Analysis]:
        return self.session.query(Analysis).filter(Analysis.plate_id == plate_id).all()

    def get_analysis_by_type_sample(
        self,
        sample_id: str,
        analysis_type: str,
    ) -> Analysis | None:
        return (
            self.session.query(Analysis)
            .filter(Analysis.sample_id == sample_id, Analysis.type == analysis_type)
            .first()
        )

    def get_analysis_by_id(self, analysis_id: int) -> Analysis:
        return self.session.query(Analysis).filter(Analysis.id == analysis_id).one()

    def get_analyses(self) -> list[Analysis]:
        return self.session.query(Analysis).all()

    def get_analyses_with_skip_and_limit(self, skip: int, limit: int) -> list[Analysis]:
        return self.session.query(Analysis).offset(skip).limit(limit).all()

    def get_analyses_by_type_between_dates(
        self, analysis_type: str, date_min: date, date_max: date
    ) -> list[Analysis]:
        return (
            self.session.query(Analysis)
            .filter(
                Analysis.type == analysis_type,
                Analysis.created_at > date_min - timedelta(days=1),
                Analysis.created_at < date_max + timedelta(days=1),
            )
            .all()
        )

    def get_analysis_by_type_and_sample_id(self, analysis_type: str, sample_id: str) -> Analysis:
        return (
            self.session.query(Analysis)
            .filter(Analysis.sample_id == sample_id, Analysis.type == analysis_type)
            .one()
        )

    def get_plate_by_id(self, plate_id: int) -> Plate:
        return self.session.query(Plate).filter(Plate.id == plate_id).one()

    def get_plate_by_plate_id(self, plate_id: str) -> Plate:
        return self.session.query(Plate).filter(Plate.plate_id == plate_id).one()

    def get_ordered_plates(self, order_params: PlateOrderParams) -> list[Plate]:
        sort_func = desc if order_params.sort_order == "descend" else asc
        return (
            self.session.query(Plate)
            .order_by(sort_func(order_params.order_by))
            .offset(order_params.skip)
            .limit(order_params.limit)
            .all()
        )

    def get_incomplete_samples(query: Query) -> Query:
        """Returning sample query statement for samples with less than two analyses."""
        return (
            query.group_by(Analysis.sample_id)
            .order_by(Analysis.created_at)
            .having(func.count(Analysis.sample_id) < 2)
        )

    def get_filtered_samples(self, filter_params: SampleFilterParams) -> list[Sample]:
        query = self.session.query(Sample).distinct().join(Analysis)
        if filter_params.sample_id:
            query = self.get_samples(query, filter_params.sample_id)
        if filter_params.plate_id:
            query = self.get_plate_samples(query, filter_params.plate_id)
        if filter_params.is_incomplete:
            query = self.get_incomplete_samples(query)
        if filter_params.is_commented:
            query = self.get_commented_samples(query)
        if filter_params.is_missing:
            query = self.get_status_missing_samples(query)
        return (
            query.order_by(Sample.created_at.desc())
            .offset(filter_params.skip)
            .limit(filter_params.limit)
            .all()
        )

    def get_plate_samples(query: Query, plate_id: str) -> Query:
        """Returning sample query statement for samples analysed on a specific plate."""
        return query.filter(Analysis.plate_id == plate_id)

    def get_commented_samples(query: Query) -> Query:
        """Returning sample query statement for samples with no comment."""
        return query.filter(Sample.comment != None)

    def get_status_missing_samples(query: Query) -> Query:
        """Returning sample query statement for samples with no comment."""
        return query.filter(Sample.status == None)

    def get_sample(self, sample_id: str) -> Sample:
        """Get sample or raise 404."""
        return self.session.query(Sample).filter(Sample.id == sample_id).one()

    def get_samples(query: Query, sample_id: str) -> Query:
        """Returns a query for samples containing the given sample_id."""
        return query.filter(Sample.id.contains(sample_id))

    def get_user_by_id(self, user_id: int) -> User:
        return self.session.query(User).filter(User.id == user_id).one()

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter(User.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.session.query(User).offset(skip).limit(limit).all()

    def get_users_with_skip_and_limit(self, skip: int, limit: int) -> list[User]:
        return self.session.query(User).offset(skip).limit(limit).all()

    def check_analyses_objects(self, analyses: list[Analysis], analysis_type: Types) -> None:
        """Raising 400 if any analysis in the list already exist in the database"""
        for analysis_obj in analyses:
            existing_analysis = self.get_analysis_by_type_sample(
                sample_id=analysis_obj.sample_id,
                analysis_type=analysis_type,
            )
            if existing_analysis:
                self.session.delete(existing_analysis)

    def get_snps(self) -> list[SNP]:
        return self.session.query(SNP).all()

    def get_snps_by_limit_and_skip(self, skip: int, limit: int) -> list[SNP]:
        return self.session.query(SNP).offset(skip).limit(limit).all()
