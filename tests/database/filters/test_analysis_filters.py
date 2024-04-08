"""Module to test the analysis filters."""

from sqlalchemy.orm import Query

from genotype_api.database.filters.analysis_filter import (
    filter_analyses_by_id,
    filter_analyses_by_type,
    filter_analyses_by_plate_id,
    filter_analyses_by_sample_id,
)
from genotype_api.database.models import Analysis
from genotype_api.database.store import Store
from tests.store_helpers import StoreHelpers


def test_filter_analyses_by_id(base_store: Store, test_analysis, helpers):
    # GIVEN an analysis

    # WHEN filtering analyses by id
    query: Query = base_store._get_query(Analysis)
    analyses: list[Analysis] = filter_analyses_by_id(
        analysis_id=test_analysis.id, analyses=query
    ).all()

    # THEN assert the analysis is returned
    assert analyses
    assert analyses[0].id == test_analysis.id


def test_filter_analyses_by_type(base_store: Store, test_analysis: Analysis, helpers: StoreHelpers):
    # GIVEN an analysis

    # WHEN filtering analyses by type
    query: Query = base_store._get_query(Analysis)

    analyses: list[Analysis] = filter_analyses_by_type(
        type=test_analysis.type, analyses=query
    ).all()

    # THEN assert the analysis is returned
    assert analyses
    assert analyses[0].type == test_analysis.type


def test_filter_analyses_by_plate_id(
    base_store: Store, test_analysis: Analysis, helpers: StoreHelpers
):
    # GIVEN an analysis

    # WHEN filtering analyses by plate id
    query: Query = base_store._get_query(Analysis)
    analyses: list[Analysis] = filter_analyses_by_plate_id(
        plate_id=test_analysis.plate_id, analyses=query
    ).all()

    # THEN assert the analysis is returned
    assert analyses
    assert analyses[0].plate_id == test_analysis.plate_id


def test_filter_analyses_by_sample_id(base_store: Store, test_analysis, helpers):
    # GIVEN an analysis

    # WHEN filtering analyses by sample id
    query: Query = base_store._get_query(Analysis)
    analyses: list[Analysis] = filter_analyses_by_sample_id(
        sample_id=test_analysis.sample_id, analyses=query
    ).all()

    # THEN assert the analysis is returned
    assert analyses
    assert analyses[0].sample_id == test_analysis.sample_id
