"""Module to test the delete functionality of the genotype API CRUD."""

from sqlalchemy.orm import Query

from genotype_api.database.models import SNP, Analysis, Plate, Sample, User
from genotype_api.database.store import Store


async def test_delete_analysis(base_store: Store, test_analysis: Analysis):
    # GIVEN an analysis and a store with the analysis
    analyses = await base_store.get_analyses()
    assert test_analysis in analyses

    # WHEN deleting the analysis
    await base_store.delete_analysis(analysis=test_analysis)

    # THEN the analysis is deleted
    analyses = await base_store.get_analyses()
    assert test_analysis not in analyses


async def test_delete_sample(base_store: Store, test_sample: Sample):
    # GIVEN a sample and a store with the sample
    query: Query = base_store._get_query(Sample)
    result = await base_store.session.execute(query)
    assert test_sample in result.scalars().all()

    # WHEN deleting the sample
    await base_store.delete_sample(sample=test_sample)

    # THEN the sample is deleted
    result = await base_store.session.execute(base_store._get_query(test_sample))
    assert test_sample not in result.scalars().all()


async def test_delete_plate(base_store: Store, test_plate: Plate):
    # GIVEN a plate and a store with the plate
    result = await base_store.session.execute(base_store._get_query(test_plate))
    assert test_plate in result.scalars().all()

    # WHEN deleting the plate
    await base_store.delete_plate(plate=test_plate)

    # THEN the plate is deleted
    result = await base_store.session.execute(base_store._get_query(test_plate))
    assert test_plate not in result.scalars().all()


async def test_delete_user(base_store: Store, test_user: User):
    # GIVEN a user and a store with the user
    result = await base_store.session.execute(base_store._get_query(test_user))
    assert test_user in result.scalars().all()

    # WHEN deleting the user
    base_store.delete_user(user=test_user)

    # THEN the user is deleted
    result = await base_store.session.execute(base_store._get_query(test_user))
    assert test_user not in result.scalars().all()


async def test_delete_snps(base_store: Store, test_snp: SNP):
    # GIVEN an SNP and a store with the SNP
    result = await base_store.session.execute(base_store._get_query(test_snp))
    assert result.scalars().all()

    # WHEN deleting the SNP
    base_store.delete_snps()

    # THEN all SNPs are deleted
    result = await base_store.session.execute(base_store._get_query(test_snp))
    assert not result.scalars().all()
