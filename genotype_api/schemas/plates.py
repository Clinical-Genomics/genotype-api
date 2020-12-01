"""Plate schemas"""

from typing import List

from pydantic import BaseModel

from .analysis import Analysis


class PlateBase(BaseModel):
    plate_id: str


class PlateCreate(PlateBase):
    pass


class Plate(PlateBase):
    id: int
    analyses: List[Analysis]

    class Config:
        orm_mode = True
