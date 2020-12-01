"""Analysis schemas"""

from typing import Optional

from pydantic import BaseModel


class AnalysisBase(BaseModel):
    type: str
    source: Optional[str]
    sample_id: str


class AnalysisCreate(AnalysisBase):
    pass


class Analysis(AnalysisBase):
    id: int
    sex: Optional[str]
    plate_id: Optional[int] = None

    class Config:
        orm_mode = True
