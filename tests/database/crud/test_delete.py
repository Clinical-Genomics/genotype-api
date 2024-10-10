"""Module to test the delete functionality of the genotype API CRUD."""

from sqlalchemy.future import select
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
    query: Query = select(Sample)
    sample = await base_store.fetch_all_rows(query)
    assert test_sample in sample

    # WHEN deleting the sample
    await base_store.delete_sample(sample=test_sample)

    # THEN the sample is deleted
    sample = await base_store.fetch_all_rows(query)
    assert test_sample not in sample


async def test_delete_plate(base_store: Store, test_plate: Plate):
    # GIVEN a plate and a store with the plate
    query: Query = select(Plate)
    plate = await base_store.fetch_all_rows(query)
    assert test_plate in plate

    # WHEN deleting the plate
    await base_store.delete_plate(plate=test_plate)

    # THEN the plate is deleted
    plate = await base_store.fetch_all_rows(query)
    assert test_plate not in plate


async def test_delete_user(base_store: Store, test_user: User):
    # GIVEN a user and a store with the user
    query: Query = select(User)
    user = await base_store.fetch_all_rows(query)
    assert test_user in user

    # WHEN deleting the user
    base_store.delete_user(user=test_user)

    # THEN the user is deleted
    user = await base_store.fetch_all_rows(query)
    assert test_user not in user


async def test_delete_snps(base_store: Store, test_snp: SNP):
    # GIVEN an SNP and a store with the SNP
    query: Query = select(SNP)
    snp = await base_store.fetch_all_rows(query)
    assert snp

    # WHEN deleting the SNP
    base_store.delete_snps()

    # THEN all SNPs are deleted
    snp = await base_store.fetch_all_rows(query)
    assert not snp
