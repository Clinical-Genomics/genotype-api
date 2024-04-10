"""Module to test the delete functionality of the genotype API CRUD."""

from genotype_api.database.models import Analysis, Sample, User, Plate, SNP
from genotype_api.database.store import Store


def test_delete_analysis(base_store: Store, test_analysis: Analysis):
    # GIVEN an analysis and a store with the analysis
    assert test_analysis in base_store._get_query(Analysis).all()

    # WHEN deleting the analysis
    base_store.delete_analysis(analysis=test_analysis)

    # THEN the analysis is deleted
    assert test_analysis not in base_store._get_query(Analysis).all()


def test_delete_sample(base_store: Store, test_sample: Sample):
    # GIVEN a sample and a store with the sample
    assert test_sample in base_store._get_query(Sample).all()

    # WHEN deleting the sample
    base_store.delete_sample(sample=test_sample)

    # THEN the sample is deleted
    assert test_sample not in base_store._get_query(Sample).all()


def test_delete_plate(base_store: Store, test_plate: Plate):
    # GIVEN a plate and a store with the plate
    assert test_plate in base_store._get_query(Plate).all()

    # WHEN deleting the plate
    base_store.delete_plate(plate=test_plate)

    # THEN the plate is deleted
    assert test_plate not in base_store._get_query(Plate).all()


def test_delete_user(base_store: Store, test_user: User):
    # GIVEN a user and a store with the user
    assert test_user in base_store._get_query(User).all()

    # WHEN deleting the user
    base_store.delete_user(user=test_user)

    # THEN the user is deleted
    assert test_user not in base_store._get_query(User).all()


def test_delete_snps(base_store: Store, test_snp: SNP):
    # GIVEN an SNP and a store with the SNP
    assert base_store._get_query(SNP).all()

    # WHEN deleting the SNP
    base_store.delete_snps()

    # THEN all SNPs are deleted
    assert not base_store._get_query(SNP).all()
