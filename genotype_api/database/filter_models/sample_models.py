"""Module to hold the models for sample queries."""

from pydantic import BaseModel, Field

from genotype_api.constants import Sexes


class SampleFilterParams(BaseModel):
    sample_id: str | None = None
    plate_id: str | None = None
    is_incomplete: bool | None = None
    is_commented: bool | None = None
    is_missing: bool | None = None
    skip: int
    limit: int


class SampleSexesUpdate(BaseModel):
    sample_id: str
    sex: Sexes
    genotype_sex: Sexes
    sequence_sex: Sexes
