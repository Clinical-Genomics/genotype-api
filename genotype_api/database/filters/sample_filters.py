"""Module for the sample filters."""

from enum import Enum
from typing import Callable
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from sqlalchemy.orm import Query

from genotype_api.database.models import Sample, Analysis


def filter_samples_by_id(sample_id: str, samples: Query, **kwargs) -> Query:
    """Return sample by id."""
    return samples.filter(Sample.id == sample_id)


def filter_samples_having_comment(samples: Query, is_commented: bool | None, **kwargs) -> Query:
    """Return sample with a comment."""
    return samples.filter(Sample.comment.isnot(None)) if is_commented else samples


def filter_samples_without_status(samples: Query, is_missing: bool | None, **kwargs) -> Query:
    """Return samples without a status."""
    return samples.filter(Sample.status.is_(None)) if is_missing else samples


def filter_samples_contain_id(sample_id: str | None, samples: Query, **kwargs) -> Query:
    """Return sample by id."""
    return samples.filter(Sample.id.contains(sample_id)) if sample_id else samples


def filter_incomplete_samples(samples: Query, is_incomplete: bool | None, **kwargs) -> Query:
    return (
        (
            samples.group_by(Analysis.sample_id)
            .order_by(Analysis.created_at)
            .having(func.count(Analysis.sample_id) < 2)
        )
        if is_incomplete
        else samples
    )


def filter_samples_analysed_on_plate(samples: Query, plate_id: str | None, **kwargs) -> Query:
    """
    Return samples analysed on a plate.
    Requires a Sample and Analysis table join to work.
    """
    return samples.filter(Analysis.plate_id == plate_id) if plate_id else samples


def add_skip_and_limit(samples: Query, skip: int, limit: int, **kwargs) -> Query:
    """Add skip and limit to the query."""
    return samples.offset(skip).limit(limit)


def apply_sample_filter(
    filter_functions: list[Callable],
    samples: Query,
    sample_id: str = None,
    plate_id: str = None,
    is_commented: bool | None = None,
    is_missing: bool | None = None,
    is_incomplete: bool | None = None,
    skip: int = None,
    limit: int = None,
) -> Query:
    """Apply filtering functions to the sample queries and return filtered results."""
    for filter_function in filter_functions:
        samples: Query = filter_function(
            samples=samples,
            sample_id=sample_id,
            plate_id=plate_id,
            is_commented=is_commented,
            is_missing=is_missing,
            is_incomplete=is_incomplete,
            skip=skip,
            limit=limit,
        )
        return samples


class SampleFilter(Enum):
    """Define Sample filter functions."""

    BY_ID: Callable = filter_samples_by_id
    CONTAINS_ID: Callable = filter_samples_contain_id
    HAVING_COMMENT: Callable = filter_samples_having_comment
    WITHOUT_STATUS: Callable = filter_samples_without_status
    INCOMPLETE: Callable = filter_incomplete_samples
    ANALYSED_ON_PLATE: Callable = filter_samples_analysed_on_plate
    SKIP_AND_LIMIT: Callable = add_skip_and_limit
