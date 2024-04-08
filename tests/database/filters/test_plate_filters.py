"""Module to test the plate filters."""

from genotype_api.database.filters.plate_filters import (
    filter_plates_by_id,
    filter_plates_by_plate_id,
)
from genotype_api.database.models import Plate
from genotype_api.database.store import Store


def test_filter_plates_by_id(base_store: Store, test_plate: Plate):
    """Test filtering plates by id."""
    # GIVEN a store with a plate

    # WHEN filtering plates by id
    query = base_store._get_query(Plate)
    plate = filter_plates_by_id(entry_id=test_plate.id, plates=query).first()

    # THEN the plate is returned
    assert plate
    assert plate.id == test_plate.id


def test_filter_plates_by_plate_id(base_store: Store, test_plate: Plate):
    """Test filtering plates by plate id."""
    # GIVEN a store with a plate

    # WHEN filtering plates by plate id
    query = base_store._get_query(Plate)
    plate = filter_plates_by_plate_id(plate_id=test_plate.plate_id, plates=query).first()

    # THEN the plate is returned
    assert plate
    assert plate.plate_id == test_plate.plate_id
