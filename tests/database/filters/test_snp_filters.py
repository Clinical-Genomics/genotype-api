"""Module to test the SNP filters."""

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
    query: Query = base_store._get_query(SNP)
    filter_functions = filter_snps_by_id(snp_id=test_snp.id, snps=query)
    filtered_query = apply_snp_filter(
        snps=query, filter_functions=filter_functions, snp_id=test_snp.id
    )
    result = await base_store.session.execute(filtered_query)
    snp: SNP = result.scalars().first()

    # THEN the SNP is returned
    assert snp
    assert snp.id == test_snp.id


async def test_add_skip_and_limit(base_store: Store, test_snp: SNP):
    """Test add_skip_and_limit function."""

    # GIVEN a store with two SNPs
    assert len(await base_store._get_query(SNP).all()) == 2

    # WHEN adding skip and limit to the query
    query: Query = base_store._get_query(SNP)
    filtered_query = add_skip_and_limit(query, skip=0, limit=1)
    result = await base_store.session.execute(filtered_query)
    snps: list[SNP] = result.scalars().all()

    # THEN one SNP is returned
    assert snps
    assert len(snps) == 1
