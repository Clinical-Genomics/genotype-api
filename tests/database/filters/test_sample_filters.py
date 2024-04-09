"""Module to test the sample filters."""

from sqlalchemy.orm import Query

from genotype_api.database.filters.sample_filters import (
    filter_samples_by_id,
    filter_samples_contain_id,
    filter_samples_having_comment,
    filter_samples_without_status,
)
from genotype_api.database.models import Sample
from genotype_api.database.store import Store


def test_filter_samples_by_id(base_store: Store, test_sample: Sample):
    """Test filtering samples by id."""
    # GIVEN a store with a sample

    # WHEN filtering samples by id
    query: Query = base_store._get_query(Sample)
    sample: Sample = filter_samples_by_id(sample_id=test_sample.id, samples=query).first()

    # THEN the sample is returned
    assert sample
    assert sample.id == test_sample.id


def test_filter_samples_contain_id(base_store: Store, test_sample: Sample):
    """Test filtering samples by id."""
    # GIVEN a store with a sample

    # WHEN filtering samples by id
    query: Query = base_store._get_query(Sample)
    sample: Sample = filter_samples_contain_id(sample_id=test_sample.id, samples=query).first()

    # THEN the sample is returned
    assert sample
    assert sample.id == test_sample.id


def test_filter_samples_having_comment(base_store: Store, test_sample: Sample):
    """Test filtering samples by having comment."""
    # GIVEN a store with a sample

    # WHEN filtering samples by having comment
    query: Query = base_store._get_query(Sample)
    sample: Sample = filter_samples_having_comment(samples=query).first()

    # THEN the sample is returned
    assert sample
    assert sample.comment is not None


def test_filter_samples_without_status(base_store: Store, test_sample: Sample):
    """Test filtering samples by having comment."""
    # GIVEN a store with a sample that has a comment

    # WHEN filtering samples by having comment
    query: Query = base_store._get_query(Sample)
    sample: Sample = filter_samples_without_status(samples=query).first()

    # THEN no sample is returned
    assert not sample
