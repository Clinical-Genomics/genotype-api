"""Module for the plate dtos."""

from collections import Counter

from pydantic import BaseModel, validator

from genotype_api.models import PlateStatusCounts


class PlateResponse(BaseModel):
    pass


class PlateWithAnalysesResponse(BaseModel):
    pass

    @validator("detail")
    def check_detail(cls, value, values):
        analyses = values.get("analyses")
        statuses = [str(analysis.sample.status) for analysis in analyses]
        commented = sum(1 for analysis in analyses if analysis.sample.comment)
        status_counts = Counter(statuses)
        return PlateStatusCounts(**status_counts, total=len(analyses), commented=commented)

    class Config:
        validate_all = True
