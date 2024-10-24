"""Module to test the SNP filters."""

from sqlalchemy.future import select
from sqlalchemy.orm import Query

from genotype_api.database.filters.snp_filters import (
    add_skip_and_limit,
    apply_snp_filter,
    filter_snps_by_id,
)
from genotype_api.database.models import SNP
from genotype_api.database.store import Store


async def test_filter_snps_by_id(base_store: Store, test_snp: SNP):
    """Test filter_snps_by_id function."""

    # GIVEN a store with a SNP

    # WHEN filtering a SNP by id
    query: Query = select(SNP)
    filtered_query = filter_snps_by_id(snp_id=test_snp.id, snps=query)
    snp: SNP = base_store.fetch_first_row(filtered_query)

    # THEN the SNP is returned
    assert snp
    assert snp.id == test_snp.id


async def test_add_skip_and_limit(base_store: Store, test_snp: SNP):
    """Test add_skip_and_limit function."""

    # GIVEN a store with two SNPs
    query: Query = select(SNP)
    snps: list[SNP] = await base_store.fetch_all_rows(query)
    assert len(snps) == 2

    # WHEN adding skip and limit to the query
    filtered_query = add_skip_and_limit(query, skip=0, limit=1)
    snps: list[SNP] = base_store.fetch_all_rows(filtered_query)

    # THEN one SNP is returned
    assert snps
    assert len(snps) == 1
