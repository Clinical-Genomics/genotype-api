"""Schemas for samples"""

from typing import List

from pydantic import BaseModel

from .analysis import Analysis


class SampleBase(BaseModel):
    id: str
    sex: str = "unknown"


class SampleCreate(SampleBase):
    pass


class Sample(SampleBase):
    status: str = None
    analyses: List[Analysis]
    comment: str = None

    class Config:
        orm_mode = True
