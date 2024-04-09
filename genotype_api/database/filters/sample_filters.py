"""Module for the sample filters."""

from enum import Enum
from typing import Callable

from sqlalchemy.orm import Query

from genotype_api.database.models import Sample


def filter_samples_by_id(sample_id: str, samples: Query, **kwargs) -> Query:
    """Return sample by id."""
    return samples.filter(Sample.id == sample_id)


def filter_samples_contain_id(sample_id: str, samples: Query, **kwargs) -> Query:
    """Return sample by id."""
    return samples.filter(Sample.id.contains(sample_id))


def filter_samples_having_comment(samples: Query, **kwargs) -> Query:
    """Return sample with a comment."""
    return samples.filter(Sample.comment.isnot(None))


def filter_samples_without_status(samples: Query, **kwargs) -> Query:
    """Return samples without a status."""
    return samples.filter(Sample.status.is_(None))


def apply_sample_filter(
    filter_functions: list[Callable],
    samples: Query,
    sample_id: str,
) -> Query:
    """Apply filtering functions to the sample queries and return filtered results."""

    for filter_function in filter_functions:
        samples: Query = filter_function(
            samples=samples,
            sample_id=sample_id,
        )
    return samples


class SampleFilter(Enum):
    """Define Sample filter functions."""

    BY_ID: Callable = filter_samples_by_id
    CONTAIN_ID: Callable = filter_samples_contain_id
    HAVING_COMMENT: Callable = filter_samples_having_comment
    WITHOUT_STATUS: Callable = filter_samples_without_status
