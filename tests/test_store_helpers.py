"""Module to test the store helpers."""

from genotype_api.database.models import Plate, User, SNP, Analysis, Genotype, Sample
from genotype_api.database.store import Store
from tests.store_helpers import StoreHelpers


def test_ensure_user(helpers: StoreHelpers, store: Store, test_user: User, test_plate: Plate):

    # GIVEN a user and plates

    # WHEN ensuring a user
    helpers.ensure_user(store=store, user=test_user, plates=[test_plate])

    # THEN a user and the associated plates are added
    added_user: User = store.get_user_by_email(test_user.email)
    assert added_user

    added_plate: Plate = store.get_plate_by_id(test_plate.id)
    assert added_plate
    assert added_plate.signed_by == test_user.id


def test_ensure_snp(store: Store, helpers: StoreHelpers, test_snp: SNP):
    # GIVEN a snp

    # WHEN adding a snp to the store
    helpers.ensure_snp(store=store, snp=test_snp)

    # THEN a snp is added
    snp: SNP = store.get_snps()[0]
    assert snp
    assert snp.id == test_snp.id


def test_ensure_plate(
    store: Store,
    helpers: StoreHelpers,
    test_plate: Plate,
    test_user: User,
    test_analysis: Analysis,
):
    # GIVEN plates, a user and analyses

    # WHEN adding a plate to the store
    helpers.ensure_plate(store=store, plate=test_plate, analyses=[test_analysis], user=test_user)

    # THEN a plate and associated user and analyses are added
    added_user: User = store.get_user_by_email(test_user.email)
    assert added_user

    added_analysis: Analysis = store.get_analysis_by_id(test_analysis.id)
    assert added_analysis

    added_plate: Plate = store.get_plate_by_id(test_plate.id)
    assert added_plate


def test_ensure_genotype(
    store: Store, helpers: StoreHelpers, test_genotype: Genotype, test_analysis: Analysis
):
    # GIVEN a genotype and an associated analysis

    # WHEN adding a genotype and analysis to the store
    helpers.ensure_genotype(store=store, genotype=test_genotype, analysis=test_analysis)

    # THEN a genotype and analysis has been added
    added_genotype: Genotype = store.get_genotype_by_id(test_genotype.id)
    assert added_genotype

    added_analysis: Analysis = store.get_analysis_by_id(test_analysis.id)
    assert added_analysis


def test_ensure_analysis(
    store: Store,
    helpers: StoreHelpers,
    test_analysis: Analysis,
    test_sample: Sample,
    test_plate: Plate,
    test_genotype: Genotype,
):
    # GIVEN an analysis, sample, plate and genotypes

    # WHEN adding an analysis to the store
    helpers.ensure_analysis(
        store=store,
        analysis=test_analysis,
        sample=test_sample,
        plate=test_plate,
        genotypes=[test_genotype],
    )

    # THEN an analysis and associated sample, plate and genotypes are added
    added_analysis: Analysis = store.get_analysis_by_id(test_analysis.id)
    assert added_analysis

    added_sample: Sample = store.get_sample_by_id(test_sample.id)
    assert added_sample

    added_plate: Plate = store.get_plate_by_id(test_plate.id)
    assert added_plate

    added_genotype: Genotype = store.get_genotype_by_id(test_genotype.id)
    assert added_genotype


def test_ensure_sample(store: Store, test_sample: Sample, helpers: StoreHelpers):
    # GIVEN a sample

    # WHEN adding a sample to the store
    helpers.ensure_sample(store=store, sample=test_sample)

    # THEN a sample is added
    added_sample: Sample = store.get_sample_by_id(test_sample.id)
    assert added_sample
