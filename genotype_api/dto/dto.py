from pydantic import constr


from genotype_api.database import models


class SNPRead(models.SNPBase):
    id: constr(max_length=32)


class PlateCreate(models.PlateBase):
    analyses: list[models.Analysis] | None = []
