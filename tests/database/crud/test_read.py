"""Module to test the read functionality of the genotype API CRUD."""

from datetime import date

from genotype_api.database.filter_models.plate_models import PlateOrderParams
from genotype_api.database.models import Analysis, Plate, SNP, User, Genotype
from genotype_api.database.store import Store
from tests.store_helpers import StoreHelpers


def test_get_analysis_by_plate_id(base_store: Store, test_analysis: Analysis):
    # GIVEN an analysis and a store with the analysis

    # WHEN getting the analysis by plate id
    analyses: list[Analysis] = base_store.get_analyses_from_plate(plate_id=test_analysis.plate_id)

    # THEN the analysis is returned
    for analysis in analyses:
        assert analysis.plate_id == test_analysis.plate_id


def test_get_analysis_by_type_and_sample_id(base_store: Store, test_analysis: Analysis):
    # GIVEN an analysis and a store with the analysis

    # WHEN getting the analysis by type and sample id
    analysis: Analysis = base_store.get_analysis_by_type_and_sample_id(
        analysis_type=test_analysis.type, sample_id=test_analysis.sample_id
    )

    # THEN the analysis is returned
    assert analysis.sample_id == test_analysis.sample_id
    assert analysis.type == test_analysis.type


def test_get_analysis_by_id(base_store: Store, test_analysis: Analysis):
    # GIVEN an analysis and a store with the analysis

    # WHEN getting the analysis by id
    analysis = base_store.get_analysis_by_id(analysis_id=test_analysis.id)

    # THEN the analysis is returned
    assert analysis.id == test_analysis.id


def test_get_analyses(base_store: Store, test_analyses: list[Analysis]):
    # GIVEN an analysis and a store with the analysis

    # WHEN getting the analyses
    analyses = base_store.get_analyses()

    # THEN the analyses are returned
    assert analyses == test_analyses


def test_get_analyses_with_skip_and_limit(base_store: Store, test_analyses: list[Analysis]):
    # GIVEN an analysis and a store with the analysis

    # WHEN getting the analyses with skip and limit
    analyses = base_store.get_analyses_with_skip_and_limit(skip=0, limit=2)

    # THEN the analyses are returned
    assert analyses == test_analyses[:2]


def test_get_analyses_by_type_between_dates(
    base_store: Store,
    test_analysis: Analysis,
    date_tomorrow: date,
    date_yesterday: date,
    date_two_weeks_future: date,
    helpers: StoreHelpers,
):
    # GIVEN an analysis and a store with the analysis and the same analysis type with a different date
    future_analysis: Analysis = test_analysis
    future_analysis.created_at = date_two_weeks_future
    helpers.ensure_analysis(store=base_store, analysis=future_analysis)

    # WHEN getting the analyses by type between dates
    analyses: list[Analysis] = base_store.get_analyses_by_type_between_dates(
        analysis_type=test_analysis.type, date_min=date_yesterday, date_max=date_tomorrow
    )

    # THEN the analyses are returned
    for analysis in analyses:
        assert analysis.type == test_analysis.type
        assert analysis.created_at != date_two_weeks_future


def test_get_plate_by_id(base_store: Store, test_plate: Plate):
    # GIVEN a plate and a store with the plate

    # WHEN getting the plate by id
    plate = base_store.get_plate_by_id(plate_id=test_plate.id)

    # THEN the plate is returned
    assert plate.id == test_plate.id


def test_get_plate_by_plate_id(base_store: Store, test_plate: Plate):
    # GIVEN a plate and a store with the plate

    # WHEN getting the plate by plate id
    plate = base_store.get_plate_by_plate_id(plate_id=test_plate.plate_id)

    # THEN the plate is returned
    assert plate.plate_id == test_plate.plate_id


def get_user_by_id(base_store: Store, test_user: User):
    # GIVEN a user and a store with the user

    # WHEN getting the user by id
    user = base_store.get_user_by_id(user_id=test_user.id)

    # THEN the user is returned
    assert user.id == test_user.id


def get_user_by_email(base_store: Store, test_user: User):
    # GIVEN a user and a store with the user

    # WHEN getting the user by email
    user = base_store.get_user_by_email(email=test_user.email)

    # THEN the user is returned
    assert user.email == test_user.email


def get_user_with_skip_and_limit(base_store: Store, test_user: User):
    # GIVEN a user and a store with the user

    # WHEN getting the user with skip and limit
    user = base_store.get_users_with_skip_and_limit(skip=0, limit=2)

    # THEN the user is returned
    assert user == test_user[:2]


def test_get_genotype_by_id(base_store: Store, test_genotype: Genotype):
    # GIVEN a genotype and a store with the genotype

    # WHEN getting the genotype by id
    genotype = base_store.get_genotype_by_id(entry_id=test_genotype.id)

    # THEN the genotype is returned
    assert genotype.id == test_genotype.id


def test_get_snps(base_store: Store, test_snps: list[SNP]):
    # GIVEN a SNP and a store with the SNP

    # WHEN getting the SNPs
    snps = base_store.get_snps()

    # THEN the SNPs are returned
    assert len(snps) == len(test_snps)


def test_get_snps_by_limit_and_skip(base_store: Store, test_snps: list[SNP]):
    # GIVEN a SNP and a store with the SNP

    # WHEN getting the SNPs
    snps = base_store.get_snps_by_limit_and_skip(skip=0, limit=2)

    # THEN the SNPs are returned
    assert len(snps) == len(test_snps)


def test_get_ordered_plates(base_store: Store, test_plates: list[Plate], helpers: StoreHelpers):
    # GIVEN a plate and a store with the plate and plate order params and a plate not fulfilling the limit
    plate_order_params = PlateOrderParams(sort_order="acs", order_by="plate_id", skip=0, limit=2)
    out_of_limit_plate: Plate = test_plates[0]
    out_of_limit_plate.plate_id = "ID3"
    out_of_limit_plate.id = 3
    helpers.ensure_plate(store=base_store, plate=out_of_limit_plate)
    # WHEN getting the ordered plates

    plates = base_store.get_ordered_plates(order_params=plate_order_params)
    # THEN the plates are returned
    assert len(plates) == len(test_plates)