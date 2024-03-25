"""Module to holds models used for plate queries."""

from datetime import datetime
from typing import Callable

from pydantic import BaseModel


class PlateSignOff(BaseModel):
    user_id: int | None = None
    signed_at: datetime = datetime.now()
    method_document: str | None = None
    method_version: str | None = None


class PlateOrderParams(BaseModel):
    sort_order: str | None = None
    skip: int | None = None
    limit: int | None = None
    order_by: str | None = None
