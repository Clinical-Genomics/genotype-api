import logging

from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.models import SNP, Analysis, Genotype, Plate, Sample, User
from genotype_api.dto.user import UserRequest
from genotype_api.exceptions import SampleExistsError

LOG = logging.getLogger(__name__)


class CreateHandler(BaseHandler):

    async def create_analysis(self, analysis: Analysis) -> Analysis:
        self.session.add(analysis)
        await self.session.commit()
        await self.session.refresh(analysis)
        return analysis

    async def create_plate(self, plate: Plate) -> Plate:
        self.session.add(plate)
        await self.session.commit()
        await self.session.refresh(plate)
        LOG.info(f"Creating plate with id {plate.plate_id}.")
        return plate

    async def create_sample(self, sample: Sample) -> Sample:
        """Creates a sample in the database."""
        sample_in_db = await self._get_query(Analysis).filter(Sample.id == sample.id).one_or_none()
        if sample_in_db:
            raise SampleExistsError
        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def create_analyses_samples(self, analyses: list[Analysis]) -> list[Sample]:
        """creating samples in an analysis if not already in db."""
        return [
            await self.create_sample(sample=Sample(id=analysis.sample_id))
            for analysis in analyses
            if not await self.session.query(Sample)
            .filter(Sample.id == analysis.sample_id)
            .one_or_none()
        ]

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_snps(self, snps: list[SNP]) -> list[SNP]:
        self.session.add_all(snps)
        await self.session.commit()
        return snps

    async def create_genotype(self, genotype: Genotype) -> Genotype:
        self.session.add(genotype)
        await self.session.commit()
        return genotype
