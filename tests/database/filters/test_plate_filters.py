"""Module to test the plate filters."""

from sqlalchemy.orm import Query

from genotype_api.database.filters.plate_filters import (
    apply_plate_filter,
    filter_plates_by_id,
    filter_plates_by_plate_id,
)
from genotype_api.database.models import Plate
from genotype_api.database.store import Store


async def test_filter_plates_by_id(base_store: Store, test_plate: Plate):
    """Test filtering plates by id."""
    # GIVEN a store with a plate

    # WHEN filtering plates by id
    query: Query = base_store._get_query(Plate)
    filter_functions = filter_plates_by_id(entry_id=test_plate.id, plates=query)
    filtered_query = apply_plate_filter(
        plates=query, filter_functions=filter_functions, entry_id=test_plate.id
    )
    result = await base_store.session.execute(filtered_query)
    plate: Plate = result.scalars().first()

    # THEN the plate is returned
    assert plate
    assert plate.id == test_plate.id


async def test_filter_plates_by_plate_id(base_store: Store, test_plate: Plate):
    """Test filtering plates by plate id."""
    # GIVEN a store with a plate

    # WHEN filtering plates by plate id
    query: Query = base_store._get_query(Plate)
    filter_functions = filter_plates_by_plate_id(plate_id=test_plate.id, plates=query)
    filtered_query = apply_plate_filter(
        plates=query, filter_functions=filter_functions, plate_id=test_plate.id
    )
    result = await base_store.session.execute(filtered_query)
    plate: Plate = result.scalars().first()

    # THEN the plate is returned
    assert plate
    assert plate.plate_id == test_plate.plate_id
