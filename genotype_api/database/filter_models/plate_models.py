"""Module to holds models used for plate queries."""

from datetime import datetime
from typing import Callable

from pydantic import BaseModel


class PlateSignOff(BaseModel):
    user_id: int | None
    signed_at: datetime = datetime.now()
    method_document: str | None
    method_version: str | None


class PlateOrderParams(BaseModel):
    skip: int | None
    limit: int | None
    order_by: str | None
