"""Module to hold the models for sample queries."""

from pydantic import BaseModel, Field

from genotype_api.constants import Sexes


class SampleFilterParams(BaseModel):
    sample_id: str | None
    plate_id: str | None
    is_incomplete: bool | None
    is_commented: bool | None
    is_missing: bool | None
    skip: int
    limit: int


class SampleSexesUpdate(BaseModel):
    sample_id: str
    sex: Sexes
    genotype_sex: Sexes
    sequence_sex: Sexes
