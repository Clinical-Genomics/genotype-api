"""Module for the SNP filters."""

from sqlalchemy.orm import Query

from genotype_api.database.models import SNP


def filter_snps_by_id(snp_id: str, snps: Query, **kwargs) -> Query:
    """Return SNP by id."""
    return snps.filter(SNP.id == snp_id)


def add_skip_and_limit(snps: Query, skip: int, limit: int) -> Query:
    """Add skip and limit to the query."""
    return snps.offset(skip).limit(limit)


def apply_snp_filter(
    filter_functions: list[callable],
    snps: Query,
    snp_id: int,
    skip: int,
    limit: int,
) -> Query:
    """Apply filtering functions to the SNP queries and return filtered results."""

    for filter_function in filter_functions:
        snps: Query = filter_function(
            snps=snps,
            snp_id=snp_id,
            skip=skip,
            limit=limit,
        )
    return snps


class SnpFilter:
    """Define SNP filter functions."""

    BY_ID: callable = filter_snps_by_id
    SKIP_AND_LIMIT: callable = add_skip_and_limit
