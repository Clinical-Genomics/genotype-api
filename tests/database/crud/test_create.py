"""Module to test the create functionality of the genotype API CRUD."""

from genotype_api.database.models import Analysis, SNP, User, Genotype, Sample, Plate
from genotype_api.database.store import Store


def test_create_analysis(store: Store, test_analysis: Analysis):
    # GIVEN an analysis and an empty store

    assert not store._get_query(Analysis).all()

    # WHEN creating the analysis
    store.create_analysis(analysis=test_analysis)

    # THEN the analysis is created
    assert store._get_query(Analysis).all()[0].id == test_analysis.id


def test_create_genotype(store: Store, test_genotype: Genotype):
    # GIVEN a genotype and an empty store

    assert not store._get_query(Genotype).all()

    # WHEN creating the genotype
    store.create_genotype(genotype=test_genotype)

    # THEN the genotype is created
    assert store._get_query(Genotype).all()[0].id == test_genotype.id


def test_create_snp(store: Store, test_snp: SNP):
    # GIVEN a SNP and an empty store
    assert not store._get_query(SNP).all()

    # WHEN creating the SNP
    store.create_snps(snps=[test_snp])

    # THEN the SNP is created
    assert store._get_query(SNP).all()[0].id == test_snp.id


def test_create_user(store: Store, test_user: User):
    # GIVEN a user and an empty store
    assert not store._get_query(User).all()

    # WHEN creating the user
    store.create_user(user=test_user)

    # THEN the user is created
    assert store._get_query(User).all()[0].id == test_user.id


def test_create_sample(store: Store, test_sample: Sample):
    # GIVEN a sample and an empty store
    assert not store._get_query(Sample).all()

    # WHEN creating the sample
    store.create_sample(sample=test_sample)

    # THEN the sample is created
    assert store._get_query(Sample).all()[0].id == test_sample.id


def test_create_plate(store: Store, test_plate: Plate):
    # GIVEN a plate and an empty store
    assert not store._get_query(Plate).all()

    # WHEN creating the plate
    store.create_plate(plate=test_plate)

    # THEN the plate is created
    assert store._get_query(Plate).all()[0].id == test_plate.id


def test_create_analyses_samples(store: Store, test_analysis: Analysis):
    # GIVEN an analysis in a store
    assert not store._get_query(Sample).all()
    assert not store._get_query(Analysis).all()

    store.create_analysis(test_analysis)

    # WHEN creating the analyses
    store.create_analyses_samples(analyses=[test_analysis])

    # THEN the samples are created
    sample: Sample = store._get_query(Sample).all()[0]
    assert sample
    assert sample.id == test_analysis.sample_id
