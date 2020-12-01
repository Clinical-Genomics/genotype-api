"""SNP schemas"""

from pydantic import BaseModel


class SNPBase(BaseModel):
    id: str
    ref: str
    chrom: str
    pos: int


class SNPCreate(SNPBase):
    pass


class SNP(SNPBase):
    class Config:
        orm_mode = True
