"""Module for the user filters."""

from enum import Enum
from typing import Callable
from sqlalchemy.orm import Query
from genotype_api.database.models import User


def filter_users_by_id(user_id: int, users: Query, **kwargs) -> Query:
    """Return user by id."""
    return users.filter(User.id == user_id)


def filter_users_by_email(email: str, users: Query, **kwargs) -> Query:
    """Return user by email."""
    return users.filter(User.email == email)


def filter_users_by_name(name: str, users: Query, **kwargs) -> Query:
    """Return user by name."""
    return users.filter(User.name == name)


def add_skip_and_limit(users: Query, skip: int, limit: int) -> Query:
    """Add skip and limit to the query."""
    return users.offset(skip).limit(limit)


def apply_user_filter(
    filter_functions: list[Callable],
    users: Query,
    user_id: int,
    email: str,
    name: str,
    skip: int,
    limit: int,
) -> Query:
    """Apply filtering functions to the user queries and return filtered results."""

    for filter_function in filter_functions:
        users: Query = filter_function(
            users=users,
            user_id=user_id,
            email=email,
            name=name,
            skip=skip,
            limit=limit,
        )
    return users


class UserFilter(Enum):
    """Define User filter functions."""

    BY_ID: Callable = filter_users_by_id
    BY_EMAIL: Callable = filter_users_by_email
    BY_NAME: Callable = filter_users_by_name
    SKIP_AND_LIMIT: Callable = add_skip_and_limit
