"""Module to test the create functionality of the genotype API CRUD."""

from sqlalchemy.future import select
from sqlalchemy.orm import Query

from genotype_api.database.models import SNP, Analysis, Genotype, Plate, Sample, User
from genotype_api.database.store import Store


async def test_create_analysis(store: Store, test_analysis: Analysis):
    # GIVEN an analysis and an empty store
    analyses_query: Query = select(Analysis)
    analyses = await store.fetch_all_rows(analyses_query)
    assert not analyses

    # WHEN creating the analysis
    await store.create_analysis(analysis=test_analysis)

    analyses = await store.fetch_all_rows(analyses_query)
    assert analyses[0].id == test_analysis.id


async def test_create_genotype(store: Store, test_genotype: Genotype):
    # GIVEN a genotype and an empty store
    genotypes_query: Query = select(Genotype)
    genotypes = await store.fetch_all_rows(genotypes_query)
    assert not genotypes

    # WHEN creating the genotype
    await store.create_genotype(genotype=test_genotype)

    # THEN the genotype is created
    genotypes = await store.fetch_all_rows(genotypes_query)
    assert genotypes[0].id == test_genotype.id


async def test_create_snp(store: Store, test_snp: SNP):
    # GIVEN a SNP and an empty store
    snps_query: Query = select(SNP)
    snps = await store.fetch_all_rows(snps_query)
    assert not snps

    # WHEN creating the SNP
    await store.create_snps(snps=[test_snp])

    # THEN the SNP is created
    snps = await store.fetch_all_rows(snps_query)
    assert snps[0].id == test_snp.id


async def test_create_user(store: Store, test_user: User):
    # GIVEN a user and an empty store
    users_query: Query = select(User)
    users = await store.fetch_all_rows(users_query)
    assert not users

    # WHEN creating the user
    await store.create_user(user=test_user)

    # THEN the user is created
    users = await store.fetch_all_rows(users_query)
    assert users[0].id == test_user.id


async def test_create_sample(store: Store, test_sample: Sample):
    # GIVEN a sample and an empty store
    samples_query: Query = select(Sample)
    samples = await store.fetch_all_rows(samples_query)
    assert not samples

    # WHEN creating the sample
    await store.create_sample(sample=test_sample)

    # THEN the sample is created
    samples = await store.fetch_all_rows(samples_query)
    assert samples[0].id == test_sample.id


async def test_create_plate(store: Store, test_plate: Plate):
    # GIVEN a plate and an empty store
    plates_query: Query = select(Plate)
    plates = await store.fetch_all_rows(plates_query)
    assert not plates

    # WHEN creating the plate
    await store.create_plate(plate=test_plate)

    # THEN the plate is created
    plates = await store.fetch_all_rows(plates_query)
    assert plates[0].id == test_plate.id


async def test_create_analyses_samples(store: Store, test_analysis: Analysis):
    # GIVEN an analysis in a store
    samples_query: Query = select(Sample)
    analyses_query: Query = select(Analysis)

    samples = await store.fetch_all_rows(samples_query)
    assert not samples

    analyses = await store.fetch_all_rows(analyses_query)
    assert not analyses

    await store.create_analysis(test_analysis)

    # WHEN creating the analyses samples
    await store.create_analyses_samples(analyses=[test_analysis])

    # THEN the samples are created
    sample: Sample = await store.fetch_all_rows(samples_query)[0]
    assert sample
    assert sample.id == test_analysis.sample_id
