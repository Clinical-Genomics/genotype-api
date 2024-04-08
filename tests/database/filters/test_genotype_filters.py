"""Module to test the genotype filters."""

from genotype_api.database.filters.genotype_filters import filter_genotypes_by_id


def test_filter_genotypes_by_id(store, test_genotype, helpers):
    # GIVEN a genotype
    helpers.ensure_genotype(store=store, genotype=test_genotype)

    # WHEN filtering genotypes by id
    genotypes = filter_genotypes_by_id(genotype_id=test_genotype.id)

    # THEN assert the genotype is returned
    assert genotypes
    assert genotypes[0].id == test_genotype.id
