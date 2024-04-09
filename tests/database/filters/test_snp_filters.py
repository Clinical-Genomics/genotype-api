"""Module to test the SNP filters."""

from sqlalchemy.orm import Query

from genotype_api.database.filters.snp_filters import filter_snps_by_id, add_skip_and_limit
from genotype_api.database.models import SNP
from genotype_api.database.store import Store


def test_filter_snps_by_id(base_store: Store, test_snp: SNP):
    """Test filter_snps_by_id function."""

    # GIVEN a store with a SNP

    # WHEN filtering a SNP by id
    query: Query = base_store._get_query(SNP)
    snp: SNP = filter_snps_by_id(snp_id=test_snp.id, snps=query).first()

    # THEN the SNP is returned
    assert snp
    assert snp.id == test_snp.id


def test_add_skip_and_limit(base_store: Store, test_snp: SNP):
    """Test add_skip_and_limit function."""

    # GIVEN a store with two SNPs

    # WHEN adding skip and limit to the query
    query: Query = base_store._get_query(SNP)
    snps: list[SNP] = add_skip_and_limit(query, skip=0, limit=1).all()

    # THEN one SNP is returned
    assert snps
    assert len(snps) == 1
