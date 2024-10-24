"""Module to test the plate filters."""

from sqlalchemy.future import select
from sqlalchemy.orm import Query

from genotype_api.database.filters.plate_filters import (
    filter_plates_by_id,
    filter_plates_by_plate_id,
)
from genotype_api.database.models import Plate
from genotype_api.database.store import Store


async def test_filter_plates_by_id(base_store: Store, test_plate: Plate):
    """Test filtering plates by id."""
    # GIVEN a store with a plate

    # WHEN filtering plates by id
    query: Query = select(Plate)
    filtered_query = filter_plates_by_id(entry_id=test_plate.id, plates=query)
    plate: Plate = await base_store.fetch_first_row(filtered_query)

    # THEN the plate is returned
    assert plate
    assert plate.id == test_plate.id


async def test_filter_plates_by_plate_id(base_store: Store, test_plate: Plate):
    """Test filtering plates by plate id."""
    # GIVEN a store with a plate

    # WHEN filtering plates by plate id
    query: Query = select(Plate)
    filtered_query = filter_plates_by_plate_id(plate_id=test_plate.id, plates=query)
    plate: Plate = await base_store.fetch_first_row(filtered_query)

    # THEN the plate is returned
    assert plate
    assert plate.plate_id == test_plate.plate_id
