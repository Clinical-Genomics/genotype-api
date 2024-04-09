"""Module for the plate filters."""

from sqlalchemy.orm import Query

from genotype_api.database.models import Plate


def filter_plates_by_id(entry_id: int, plates: Query, **kwargs) -> Query:
    """Return plate by id."""
    return plates.filter(Plate.id == entry_id)


def filter_plates_by_plate_id(plate_id: str, plates: Query, **kwargs) -> Query:
    """Return plate by plate id."""
    return plates.filter(Plate.plate_id == plate_id)


def add_skip_and_limit(plates: Query, skip: int, limit: int, **kwargs) -> Query:
    """Add skip and limit to the query."""
    return plates.offset(skip).limit(limit)


def order_plates(plates: Query, order_by: str, sort_func: callable, **kwargs) -> Query:
    """Order the plates by the given column."""
    return plates.order_by(sort_func(order_by))


def apply_plate_filter(
    filter_functions: list[callable],
    plates: Query = None,
    entry_id: int = None,
    plate_id: str = None,
    skip: int = None,
    limit: int = None,
    order_by: str = None,
    sort_func: callable = None,
) -> Query:
    """Apply filtering functions to the plate queries and return filtered results."""

    for filter_function in filter_functions:
        plates: Query = filter_function(
            plates=plates,
            entry_id=entry_id,
            plate_id=plate_id,
            skip=skip,
            limit=limit,
            order_by=order_by,
            sort_func=sort_func,
        )
    return plates


class PlateFilter:
    """Define Plate filter functions."""

    BY_ID: callable = filter_plates_by_id
    BY_PLATE_ID: callable = filter_plates_by_plate_id
    SKIP_AND_LIMIT: callable = add_skip_and_limit
    ORDER: callable = order_plates
