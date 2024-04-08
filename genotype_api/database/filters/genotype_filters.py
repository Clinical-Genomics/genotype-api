"""Module for the genotype filters."""

from enum import Enum

from sqlalchemy.orm import Query

from genotype_api.database.models import Genotype


def filter_genotypes_by_id(genotype_id: int, genotypes: Query, **kwargs) -> Query:
    """Return genotype by id."""
    return genotypes.filter(Genotype.id == genotype_id)


def apply_genotype_filter(
    filter_functions: list[callable],
    entry_id: int,
    genotypes: Query,
) -> Query:
    for filter_function in filter_functions:
        genotypes: Query = filter_function(genotypes=genotypes, id=id)
    return genotypes


class GenotypeFilter(Enum):
    """Enum for the genotype filters."""

    BY_ID = filter_genotypes_by_id
