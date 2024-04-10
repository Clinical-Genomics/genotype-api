"""Module to test the update functionality of the genotype API CRUD."""

from genotype_api.database.filter_models.plate_models import PlateSignOff
from genotype_api.database.filter_models.sample_models import SampleSexesUpdate
from genotype_api.database.models import Sample, Plate
from genotype_api.database.store import Store
from tests.store_helpers import StoreHelpers


def test_refresh_sample_status(store: Store, test_sample: Sample, helpers: StoreHelpers):
    # GIVEN a sample and a store with the sample with an initial status
    initial_status: str = "initial_status"
    test_sample.status = initial_status
    helpers.ensure_sample(store=store, sample=test_sample)

    # WHEN updating the sample status
    store.refresh_sample_status(sample=test_sample)

    # THEN the sample status is updated
    updated_sample = store.get_sample_by_id(sample_id=test_sample.id)
    assert updated_sample.status != initial_status


def test_update_sample_comment(store: Store, test_sample: Sample, helpers: StoreHelpers):
    # GIVEN a sample and a store with the sample
    initial_comment: str = "initial_comment"
    test_sample.comment = initial_comment
    helpers.ensure_sample(store=store, sample=test_sample)

    # WHEN updating the sample comment
    new_comment: str = "new_comment"
    store.update_sample_comment(sample_id=test_sample.id, comment=new_comment)

    # THEN the sample comment is updated
    updated_sample = store.get_sample_by_id(sample_id=test_sample.id)
    assert updated_sample.comment == new_comment


def test_update_sample_status(store: Store, test_sample: Sample, helpers: StoreHelpers):
    # GIVEN a sample and a store with the sample
    initial_status: str = "initial_status"
    test_sample.status = initial_status
    helpers.ensure_sample(store=store, sample=test_sample)

    # WHEN updating the sample status
    new_status: str = "new_status"
    store.update_sample_status(sample_id=test_sample.id, status=new_status)

    # THEN the sample status is updated
    updated_sample = store.get_sample_by_id(sample_id=test_sample.id)
    assert updated_sample.status == new_status


def test_update_user_email(store: Store, test_user, helpers: StoreHelpers):
    # GIVEN a user and a store with the user
    initial_email: str = "initial_email"
    test_user.email = initial_email
    helpers.ensure_user(store=store, user=test_user)

    # WHEN updating the user email
    new_email: str = "new_email"
    store.update_user_email(user=test_user, email=new_email)

    # THEN the user email is updated
    updated_user = store.get_user_by_id(user_id=test_user.id)
    assert updated_user.email == new_email


def test_update_plate_sign_off(
    store: Store, unsigned_plate: Plate, plate_sign_off: PlateSignOff, helpers: StoreHelpers
):
    # GIVEN a plate and a store with the plate
    helpers.ensure_plate(store=store, plate=unsigned_plate)

    # WHEN updating the plate sign off
    store.update_plate_sign_off(plate=unsigned_plate, plate_sign_off=plate_sign_off)

    # THEN the plate sign off is updated
    updated_plate = store.get_plate_by_id(plate_id=unsigned_plate.id)
    assert updated_plate.signed_by == plate_sign_off.user_id
    assert updated_plate.signed_at == plate_sign_off.signed_at
    assert updated_plate.method_document == plate_sign_off.method_document
    assert updated_plate.method_version == plate_sign_off.method_version


def test_update_sample_sex(base_store: Store, sample_sex_update: SampleSexesUpdate):
    # GIVEN a store with a sample, analysis

    # WHEN updating the sex of the sample
    base_store.update_sample_sex(sample_sex_update)

    # THEN the sex of the sample and analysis
    updated_sample = base_store.get_sample_by_id(sample_id=sample_sex_update.sample_id)
    assert updated_sample.sex == sample_sex_update.sex
    for analysis in updated_sample.analyses:
        assert analysis.sex == sample_sex_update.genotype_sex