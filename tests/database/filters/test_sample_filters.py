"""Module to test the sample filters."""

from sqlalchemy.future import select
from sqlalchemy.orm import Query

from genotype_api.database.filters.sample_filters import (
    add_skip_and_limit,
    apply_sample_filter,
    filter_samples_analysed_on_plate,
    filter_samples_by_id,
    filter_samples_contain_id,
    filter_samples_having_comment,
    filter_samples_without_status,
)
from genotype_api.database.models import Plate, Sample
from genotype_api.database.store import Store
from tests.store_helpers import StoreHelpers


async def test_filter_samples_by_id(base_store: Store, test_sample: Sample):
    """Test filtering samples by id."""
    # GIVEN a store with a sample

    # WHEN filtering samples by id
    query: Query = select(Sample)
    filtered_query = filter_samples_by_id(sample_id=test_sample.id, samples=query)
    sample: Sample = await base_store.fetch_first_row(filtered_query)

    # THEN the sample is returned
    assert sample
    assert sample.id == test_sample.id


async def test_filter_samples_contain_id(base_store: Store, test_sample: Sample):
    """Test filtering samples by id."""
    # GIVEN a store with a sample

    # WHEN filtering samples by id
    query: Query = select(Sample)
    filter_functions = filter_samples_contain_id(sample_id=test_sample.id, samples=query)
    filtered_query = apply_sample_filter(
        samples=query, filter_functions=filter_functions, sample_id=test_sample.id
    )
    sample: Sample = await base_store.fetch_first_row(filtered_query)

    # THEN the sample is returned
    assert sample
    assert sample.id == test_sample.id


async def test_filter_samples_contain_id_when_no_id(base_store: Store, test_sample: Sample):
    """Test filtering samples by id when no id is provided."""
    # GIVEN a store with two samples
    query: Query = select(Sample)
    samples: list[Sample] = await base_store.fetch_all_rows(query)
    assert len(samples) == 2

    # WHEN filtering samples by id
    filter_functions = filter_samples_contain_id(sample_id=None, samples=query)
    filtered_query = apply_sample_filter(
        samples=query, filter_functions=filter_functions, sample_id=None
    )
    samples: list[Sample] = await base_store.fetch_all_rows(filtered_query)

    # THEN all samples are returned
    assert len(samples) == 2


async def test_filter_samples_having_comment(
    base_store: Store, test_sample: Sample, helpers: StoreHelpers
):
    """Test filtering samples by having comment."""
    # GIVEN a store with samples having a comment and one without
    query: Query = select(Sample)
    samples: list[Sample] = await base_store.fetch_all_rows(query)
    assert len(samples) == 2
    sample_without_comment: Sample = test_sample
    sample_without_comment.comment = None
    sample_without_comment.id = "sample_without_status"
    await helpers.ensure_sample(store=base_store, sample=sample_without_comment)

    # WHEN filtering samples by having comment
    filter_functions = filter_samples_having_comment(samples=query, is_commented=True)
    filtered_query = apply_sample_filter(samples=query, filter_functions=filter_functions)
    samples: list[Sample] = await base_store.fetch_all_rows(filtered_query)

    # THEN samples with comments are returned
    assert samples
    for sample in samples:
        assert sample.comment


async def test_filter_samples_having_comment_none_provided(base_store: Store, test_sample: Sample):
    """Test filtering samples by having comment."""
    # GIVEN a store with samples having a comment and one without
    query: Query = select(Sample)
    samples: list[Sample] = await base_store.fetch_all_rows(query)
    assert len(samples) == 2

    # WHEN filtering samples by having comment
    filter_functions = filter_samples_having_comment(samples=query, is_commented=None)
    filtered_query = apply_sample_filter(samples=query, filter_functions=filter_functions)
    samples: list[Sample] = await base_store.fetch_all_rows(filtered_query)

    # THEN the sample is returned
    assert len(samples) == 2


async def test_filter_samples_without_status(
    base_store: Store, test_sample: Sample, helpers: StoreHelpers
):
    """Test filtering samples by having status."""
    # GIVEN a store with samples having a status and one without
    sample_without_status: Sample = test_sample
    sample_without_status.status = None
    sample_without_status.id = "sample_without_status"
    await helpers.ensure_sample(store=base_store, sample=sample_without_status)

    # WHEN filtering samples by having a status
    query: Query = select(Sample)
    filtered_query = filter_samples_without_status(samples=query, is_missing=True)
    samples: list[Sample] = await base_store.fetch_all_rows(filtered_query)

    # THEN no sample is returned
    assert samples
    for sample in samples:
        assert not sample.status


async def test_filter_samples_without_status_none_provided(base_store: Store, test_sample: Sample):
    """Test filtering samples by having status."""
    # GIVEN a store with a sample that has a status
    query: Query = select(Sample)
    samples: list[Sample] = await base_store.fetch_all_rows(query)
    assert len(samples) == 2

    # WHEN filtering samples by having a status
    query: Query = select(Sample)
    filter_functions = filter_samples_without_status(samples=query, is_missing=None)
    filtered_query = apply_sample_filter(samples=query, filter_functions=filter_functions)
    samples: list[Sample] = await base_store.fetch_all_rows(filtered_query)

    # THEN all samples are returned
    assert len(samples) == 2


async def test_filter_samples_analysed_on_plate(
    base_store: Store, test_sample: Sample, test_plate: Plate
):
    """Test filtering samples by having comment."""
    # GIVEN a store with analysed samples

    # WHEN filtering samples analysed on a plate
    query: Query = base_store._get_samples_with_analyses()
    filtered_query = filter_samples_analysed_on_plate(samples=query, plate_id=test_plate.id)
    sample: Sample = await base_store.fetch_first_row(filtered_query)

    # THEN one sample is returned
    assert sample.analyses[0].plate_id == test_plate.id


async def test_filter_samples_analysed_on_plate_none_provided(
    base_store: Store,
    test_sample: Sample,
):
    """Test filtering samples by having comment."""
    # GIVEN a store with analysed samples
    query: Query = select(Sample)
    samples: list[Sample] = await base_store.fetch_all_rows(query)
    assert len(samples) == 2

    # WHEN filtering samples analysed on a plate
    query: Query = base_store._get_samples_with_analyses()
    filtered_query = filter_samples_analysed_on_plate(samples=query, plate_id=None)
    samples: list[Sample] = await base_store.fetch_all_rows(filtered_query)

    # THEN all samples are returned
    assert len(samples) == 2


async def test_add_skip_and_limit(base_store: Store, test_sample: Sample):
    """Test add_skip_and_limit function."""
    # GIVEN a store with two samples
    query: Query = select(Sample)
    samples: list[Sample] = await base_store.fetch_all_rows(query)
    assert len(samples) == 2

    # WHEN adding skip and limit to the query
    filtered_query = add_skip_and_limit(query, skip=0, limit=1)
    samples: list[Sample] = await base_store.fetch_all_rows(filtered_query)

    # THEN one sample is returned
    assert samples
    assert len(samples) == 1
