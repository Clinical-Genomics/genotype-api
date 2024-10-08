"""Module for the analysis filters."""

from datetime import timedelta, date
from enum import Enum

from sqlalchemy.orm import Query

from genotype_api.database.models import Analysis


def filter_analyses_by_id(analysis_id: int, analyses: Query, **kwargs) -> Query:
    """Return analysis by id."""
    return analyses.filter(Analysis.id == analysis_id)


def filter_analyses_by_type(type: str, analyses: Query, **kwargs) -> Query:
    """Return analysis by type."""
    return analyses.filter(Analysis.type == type)


def filter_analyses_by_plate_id(plate_id: int, analyses: Query, **kwargs) -> Query:
    """Return analysis by plate id."""
    return analyses.filter(Analysis.plate_id == plate_id)


def filter_analyses_by_sample_id(sample_id: str, analyses: Query, **kwargs) -> Query:
    """Return analysis by sample id."""
    return analyses.filter(Analysis.sample_id == sample_id)


def add_skip_and_limit(analyses: Query, skip: int, limit: int, **kwargs) -> Query:
    """Add skip and limit to the query."""
    return analyses.offset(skip).limit(limit)


def filter_analyses_between_dates(
    analyses: Query, date_min: date, date_max: date, **kwargs
) -> Query:
    """Return analysis by type between dates."""
    return analyses.filter(
        Analysis.created_at > date_min - timedelta(days=1),
        Analysis.created_at < date_max + timedelta(days=1),
    )


def apply_analysis_filter(
    filter_functions: list[callable],
    analyses: Query,
    analysis_id: int = None,
    type: str = None,
    plate_id: int = None,
    sample_id: str = None,
    skip: int = None,
    limit: int = None,
    date_min: date = None,
    date_max: date = None,
) -> Query:
    """Apply filtering functions to the analysis queries and return filtered results."""

    for filter_function in filter_functions:
        analyses: Query = filter_function(
            analyses=analyses,
            analysis_id=analysis_id,
            type=type,
            plate_id=plate_id,
            sample_id=sample_id,
            skip=skip,
            limit=limit,
            date_min=date_min,
            date_max=date_max,
        )
    return analyses


class AnalysisFilter(Enum):
    """Define Analysis filter functions."""

    BY_ID: callable = filter_analyses_by_id
    BY_TYPE: callable = filter_analyses_by_type
    BY_PLATE_ID: callable = filter_analyses_by_plate_id
    BY_SAMPLE_ID: callable = filter_analyses_by_sample_id
    SKIP_AND_LIMIT: callable = add_skip_and_limit
    BETWEEN_DATES: callable = filter_analyses_between_dates
