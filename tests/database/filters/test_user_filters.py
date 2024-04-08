"""Module to test the user filters."""

from sqlalchemy.orm import Query

from genotype_api.database.filters.user_filters import (
    filter_users_by_id,
    filter_users_by_email,
    filter_users_by_name,
)
from genotype_api.database.models import User
from genotype_api.database.store import Store


def test_filter_users_by_id(base_store: Store, test_user: User):
    """Test filtering users by id."""
    # GIVEN a store with a user

    # WHEN filtering users by id
    query: Query = base_store._get_query(User)
    user: User = filter_users_by_id(user_id=test_user.id, users=query).first()

    # THEN the user is returned
    assert user
    assert user.id == test_user.id


def test_filter_users_by_email(base_store: Store, test_user: User):
    """Test filtering users by email."""
    # GIVEN a store with a user

    # WHEN filtering users by email
    query: Query = base_store._get_query(User)
    user: User = filter_users_by_email(email=test_user.email, users=query).first()

    # THEN the user is returned
    assert user
    assert user.email == test_user.email


def test_filter_users_by_name(base_store: Store, test_user: User):
    """Test filtering users by name."""
    # GIVEN a store with a user

    # WHEN filtering users by name
    query: Query = base_store._get_query(User)
    user: User = filter_users_by_name(name=test_user.name, users=query).first()

    # THEN the user is returned
    assert user
    assert user.name == test_user.name
