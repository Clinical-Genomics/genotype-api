"""Module to test the analysis filters."""

from sqlalchemy.orm import Query

from genotype_api.database.filters.analysis_filter import filter_analyses_by_id
from genotype_api.database.models import Analysis
from genotype_api.database.store import Store


def test_filter_analyses_by_id(base_store: Store, test_analysis, helpers):
    # GIVEN an analysis

    # WHEN filtering analyses by id
    query: Query = base_store._get_query(Analysis)
    analyses = filter_analyses_by_id(analysis_id=test_analysis.id, query=query)

    # THEN assert the analysis is returned
    assert analyses
    assert analyses[0].id == test_analysis.id


def test_filter_analyses_by_type(base_store: Store, test_analysis, helpers):
    # GIVEN an analysis

    # WHEN filtering analyses by type
    query: Query = base_store._get_query(Analysis)
    analyses = filter_analyses_by_id(analysis_id=test_analysis.type, query=query)

    # THEN assert the analysis is returned
    assert analyses
    assert analyses[0].type == test_analysis.type


def test_filter_analyses_by_plate_id(base_store: Store, test_analysis, helpers):
    # GIVEN an analysis

    # WHEN filtering analyses by plate id
    query: Query = base_store._get_query(Analysis)
    analyses = filter_analyses_by_id(analysis_id=test_analysis.plate_id, query=query)

    # THEN assert the analysis is returned
    assert analyses
    assert analyses[0].plate_id == test_analysis.plate_id


def test_filter_analyses_by_sample_id(base_store: Store, test_analysis, helpers):
    # GIVEN an analysis

    # WHEN filtering analyses by sample id
    query: Query = base_store._get_query(Analysis)
    analyses = filter_analyses_by_id(analysis_id=test_analysis.sample_id, query=query)

    # THEN assert the analysis is returned
    assert analyses
    assert analyses[0].sample_id == test_analysis.sample_id
