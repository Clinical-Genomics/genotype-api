from genotype_api.database import models


class PlateCreate(models.PlateBase):
    analyses: list[models.Analysis] | None = []
