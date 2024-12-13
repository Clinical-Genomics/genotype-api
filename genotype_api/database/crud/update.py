from pydantic import EmailStr
from sqlalchemy.future import select
from sqlalchemy.orm import Query, selectinload

from genotype_api.constants import Types
from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.filter_models.plate_models import PlateSignOff
from genotype_api.database.filter_models.sample_models import SampleSexesUpdate
from genotype_api.database.models import Analysis, Plate, Sample, User
from genotype_api.exceptions import SampleNotFoundError
from genotype_api.services.match_genotype_service.match_genotype import (
    MatchGenotypeService,
)


class UpdateHandler(BaseHandler):

    async def refresh_sample_status(
        self,
        sample: Sample,
    ) -> Sample:
        if len(sample.analyses) != 2:
            sample.status = None
        else:
            results = MatchGenotypeService.check_sample(sample=sample)
            sample.status = "fail" if "fail" in results.model_dump().values() else "pass"

        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def update_sample_comment(self, sample_id: str, comment: str) -> Sample:
        query: Query = (
            select(Sample)
            .options(selectinload(Sample.analyses).selectinload(Analysis.genotypes))
            .filter(Sample.id == sample_id)
        )
        sample: Sample = await self.fetch_one_or_none(query)

        if not sample:
            raise SampleNotFoundError

        sample.comment = comment
        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def update_sample_status(self, sample_id: str, status: str | None) -> Sample:
        query: Query = select(Sample).distinct().filter(Sample.id == sample_id)
        sample: Sample = await self.fetch_one_or_none(query)
        if not sample:
            raise SampleNotFoundError
        sample.status = status
        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def refresh_plate(self, plate: Plate) -> None:
        await self.session.refresh(plate)

    async def update_plate_sign_off(self, plate: Plate, plate_sign_off: PlateSignOff) -> Plate:
        plate.signed_by = plate_sign_off.user_id
        plate.signed_at = plate_sign_off.signed_at
        plate.method_document = plate_sign_off.method_document
        plate.method_version = plate_sign_off.method_version
        await self.session.commit()
        await self.session.refresh(plate)
        return plate

    async def update_sample_sex(self, sexes_update: SampleSexesUpdate) -> Sample:
        query: Query = (
            select(Sample)
            .distinct()
            .options(selectinload(Sample.analyses).selectinload(Analysis.genotypes))
            .join(Analysis, Analysis.sample_id == Sample.id)
            .filter(Sample.id == sexes_update.sample_id)
        )
        sample = await self.fetch_one_or_none(query)
        if not sample:
            raise SampleNotFoundError
        sample.sex = sexes_update.sex
        for analysis in sample.analyses:
            if sexes_update.genotype_sex and analysis.type == Types.GENOTYPE:
                analysis.sex = sexes_update.genotype_sex
            elif sexes_update.sequence_sex and analysis.type == Types.SEQUENCE:
                analysis.sex = sexes_update.sequence_sex
            self.session.add(analysis)
        self.session.add_all(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        sample = await self.refresh_sample_status(sample)
        return sample

    async def update_user_email(self, user: User, email: EmailStr) -> User:
        user.email = email
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
