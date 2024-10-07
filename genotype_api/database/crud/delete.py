import logging

from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.models import SNP, Analysis, Plate, Sample, User

LOG = logging.getLogger(__name__)


class DeleteHandler(BaseHandler):

    async def delete_analysis(self, analysis: Analysis) -> None:
        self.session.delete(analysis)
        await self.session.commit()

    async def delete_plate(self, plate: Plate) -> None:
        self.session.delete(plate)
        await self.session.commit()

    async def delete_sample(self, sample: Sample) -> None:
        self.session.delete(sample)
        await self.session.commit()

    async def delete_user(self, user: User) -> None:
        self.session.delete(user)
        await self.session.commit()

    async def delete_snps(self) -> int:
        query = self._get_query(SNP)
        result = await self.session.execute(query)
        snps: list[SNP] = result.scalars().all()
        count: int = len(snps)
        for snp in snps:
            self.session.delete(snp)
        await self.session.commit()
        return count
