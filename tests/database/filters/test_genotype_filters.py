"""Module to test the genotype filters."""

from sqlalchemy.orm import Query

from genotype_api.database.filters.genotype_filters import filter_genotypes_by_id
from genotype_api.database.models import Genotype
from genotype_api.database.store import Store
from tests.store_helpers import StoreHelpers


def test_filter_genotypes_by_id(store: Store, test_genotype: Genotype, helpers: StoreHelpers):
    # GIVEN a genotype
    helpers.ensure_genotype(store=store, genotype=test_genotype)

    # WHEN filtering genotypes by id
    query: Query = store._get_query(Genotype)
    genotypes: list[Genotype] = filter_genotypes_by_id(
        entry_id=test_genotype.id, genotypes=query
    ).all()

    # THEN assert the genotype is returned
    assert genotypes
    assert genotypes[0].id == test_genotype.id
