"""Module to test the create functionality of the genotype API CRUD."""

from sqlalchemy.orm import Query

from genotype_api.database.models import SNP, Analysis, Genotype, Plate, Sample, User
from genotype_api.database.store import Store


async def test_create_analysis(store: Store, test_analysis: Analysis):
    # GIVEN an analysis and an empty store
    analyses_query: Query = store._get_query(Analysis)
    result = await store.session.execute(analyses_query)
    assert not result.scalars().all()

    # WHEN creating the analysis
    await store.create_analysis(analysis=test_analysis)

    # THEN the analysis is created
    result = await store.session.execute(analyses_query)
    analyses = result.scalars().all()
    assert analyses[0].id == test_analysis.id


async def test_create_genotype(store: Store, test_genotype: Genotype):
    # GIVEN a genotype and an empty store
    genotypes_query: Query = store._get_query(Genotype)
    result = await store.session.execute(genotypes_query)
    assert not result.scalars().all()

    # WHEN creating the genotype
    await store.create_genotype(genotype=test_genotype)

    # THEN the genotype is created
    result = await store.session.execute(genotypes_query)
    genotypes = result.scalars().all()
    assert genotypes[0].id == test_genotype.id


async def test_create_snp(store: Store, test_snp: SNP):
    # GIVEN a SNP and an empty store
    snps_query: Query = store._get_query(SNP)
    result = await store.session.execute(snps_query)
    assert not result.scalars().all()

    # WHEN creating the SNP
    await store.create_snps(snps=[test_snp])

    # THEN the SNP is created
    result = await store.session.execute(snps_query)
    snps = result.scalars().all()
    assert snps[0].id == test_snp.id


async def test_create_user(store: Store, test_user: User):
    # GIVEN a user and an empty store
    users_query: Query = store._get_query(User)
    result = await store.session.execute(users_query)
    assert not result.scalars().all()

    # WHEN creating the user
    await store.create_user(user=test_user)

    # THEN the user is created
    result = await store.session.execute(users_query)
    users = result.scalars().all()
    assert users[0].id == test_user.id


async def test_create_sample(store: Store, test_sample: Sample):
    # GIVEN a sample and an empty store
    samples_query: Query = store._get_query(Sample)
    result = await store.session.execute(samples_query)
    assert not result.scalars().all()

    # WHEN creating the sample
    await store.create_sample(sample=test_sample)

    # THEN the sample is created
    result = await store.session.execute(samples_query)
    samples = result.scalars().all()
    assert samples[0].id == test_sample.id


async def test_create_plate(store: Store, test_plate: Plate):
    # GIVEN a plate and an empty store
    plates_query: Query = store._get_query(Plate)
    result = await store.session.execute(plates_query)
    assert not result.scalars().all()

    # WHEN creating the plate
    await store.create_plate(plate=test_plate)

    # THEN the plate is created
    result = await store.session.execute(plates_query)
    plates = result.scalars().all()
    assert plates[0].id == test_plate.id


async def test_create_analyses_samples(store: Store, test_analysis: Analysis):
    # GIVEN an analysis in a store
    samples_query: Query = store._get_query(Sample)
    analyses_query: Query = store._get_query(Analysis)

    result = await store.session.execute(samples_query)
    assert not result.scalars().all()

    result = await store.session.execute(analyses_query)
    assert not result.scalars().all()

    await store.create_analysis(test_analysis)

    # WHEN creating the analyses samples
    await store.create_analyses_samples(analyses=[test_analysis])

    # THEN the samples are created
    result = await store.session.execute(samples_query)
    sample: Sample = result.scalars().all()[0]
    assert sample
    assert sample.id == test_analysis.sample_id
