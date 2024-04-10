"""Module to test the sample filters."""

from sqlalchemy.orm import Query

from genotype_api.database.filters.sample_filters import (
    filter_samples_by_id,
    filter_samples_contain_id,
    filter_samples_having_comment,
    filter_samples_without_status,
    filter_samples_analysed_on_plate,
    add_skip_and_limit,
)
from genotype_api.database.models import Sample, Plate
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


def test_filter_samples_contain_id_when_no_id(base_store: Store, test_sample: Sample):
    """Test filtering samples by id when no id is provided."""
    # GIVEN a store with two samples

    # WHEN filtering samples by id
    query: Query = base_store._get_query(Sample)
    samples: list[Sample] = filter_samples_contain_id(sample_id=None, samples=query).all()

    # THEN all samples are returned
    assert len(samples) == 2


def test_filter_samples_having_comment(base_store: Store, test_sample: Sample):
    """Test filtering samples by having comment."""
    # GIVEN a store with a sample

    # WHEN filtering samples by having comment
    query: Query = base_store._get_query(Sample)
    sample: Sample = filter_samples_having_comment(samples=query, is_commented=True).first()

    # THEN the sample is returned
    assert sample
    assert sample.comment is not None


def test_filter_samples_having_comment_none_provided(base_store: Store, test_sample: Sample):
    """Test filtering samples by having comment."""
    # GIVEN a store with a sample

    # WHEN filtering samples by having comment
    query: Query = base_store._get_query(Sample)
    samples: list[Sample] = filter_samples_having_comment(samples=query, is_commented=None).all()

    # THEN the sample is returned
    assert len(samples) == 2


def test_filter_samples_without_status(base_store: Store, test_sample: Sample):
    """Test filtering samples by having comment."""
    # GIVEN a store with a sample that has a comment

    # WHEN filtering samples by having comment
    query: Query = base_store._get_query(Sample)
    sample: Sample = filter_samples_without_status(samples=query, is_missing=True).first()

    # THEN no sample is returned
    assert not sample


def test_filter_samples_without_status_none_provided(base_store: Store, test_sample: Sample):
    """Test filtering samples by having comment."""
    # GIVEN a store with a sample that has a comment

    # WHEN filtering samples by having comment
    query: Query = base_store._get_query(Sample)
    samples: list[Sample] = filter_samples_without_status(samples=query, is_missing=None).all()

    # THEN no sample is returned
    assert len(samples) == 2


def test_filter_samples_analysed_on_plate(
    base_store: Store, test_sample: Sample, test_plate: Plate
):
    """Test filtering samples by having comment."""
    # GIVEN a store with a sample that has a comment

    # WHEN filtering samples by having comment
    query: Query = base_store._get_join_analysis_on_sample()
    sample: Sample = filter_samples_analysed_on_plate(samples=query, plate_id=test_plate.id).first()

    # THEN no sample is returned
    assert sample.analyses[0].plate_id == test_plate.id


def test_filter_samples_analysed_on_plate_none_provided(
    base_store: Store,
    test_sample: Sample,
):
    """Test filtering samples by having comment."""
    # GIVEN a store with a sample that has a comment

    # WHEN filtering samples by having comment
    query: Query = base_store._get_join_analysis_on_sample()
    samples: list[Sample] = filter_samples_analysed_on_plate(samples=query, plate_id=None).all()

    # THEN no sample is returned
    assert len(samples) == 2


def test_add_skip_and_limit(base_store: Store, test_sample: Sample):
    """Test add_skip_and_limit function."""

    # GIVEN a store with two samples

    # WHEN adding skip and limit to the query
    query: Query = base_store._get_query(Sample)
    samples: list[Sample] = add_skip_and_limit(query, skip=0, limit=1).all()

    # THEN one SNP is returned
    assert samples
    assert len(samples) == 1
