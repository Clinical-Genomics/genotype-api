"""Module to test the delete functionality of the genotype API CRUD."""

from genotype_api.database.models import Analysis, Sample, User, Plate, SNP
from genotype_api.database.store import Store


def test_delete_analysis(base_store: Store, test_analysis: Analysis):
    # GIVEN an analysis and a store with the analysis
    assert base_store._get_query(Analysis).all()[0]

    # WHEN deleting the analysis
    base_store.delete_analysis(analysis=test_analysis)

    # THEN the analysis is deleted
    for analysis in base_store._get_query(Analysis).all():
        assert analysis != test_analysis


def test_delete_sample(base_store: Store, test_sample: Sample):
    # GIVEN a sample and a store with the sample
    assert base_store._get_query(Sample).all()[0]

    # WHEN deleting the sample
    base_store.delete_sample(sample=test_sample)

    # THEN the sample is deleted
    for sample in base_store._get_query(Sample).all():
        assert sample != test_sample


def test_delete_plate(base_store: Store, test_plate: Plate):
    # GIVEN a plate and a store with the plate
    assert base_store._get_query(Plate).all()[0]

    # WHEN deleting the plate
    base_store.delete_plate(plate=test_plate)

    # THEN the plate is deleted
    for plate in base_store._get_query(Plate).all():
        assert plate != test_plate


def test_delete_user(base_store: Store, test_user: User):
    # GIVEN a user and a store with the user
    assert base_store._get_query(User).all()[0]

    # WHEN deleting the user
    base_store.delete_user(user=test_user)

    # THEN the user is deleted
    for user in base_store._get_query(User).all():
        assert user != test_user


def test_delete_snps(base_store: Store, test_snp):
    # GIVEN a SNP and a store with the SNP
    assert base_store._get_query(SNP).all()[0]

    # WHEN deleting the SNP
    base_store.delete_snps()

    # THEN the SNP is deleted
    for snp in base_store._get_query(SNP).all():
        assert snp != test_snp
