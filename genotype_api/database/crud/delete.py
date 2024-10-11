import logging

from sqlalchemy.future import select

from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.models import SNP, Analysis, Plate, Sample, User

LOG = logging.getLogger(__name__)


class DeleteHandler(BaseHandler):

    async def delete_analysis(self, analysis: Analysis) -> None:
        await self.session.delete(analysis)
        await self.session.commit()

    async def delete_plate(self, plate: Plate) -> None:
        await self.session.delete(plate)
        await self.session.commit()

    async def delete_sample(self, sample: Sample) -> None:
        await self.session.delete(sample)
        await self.session.commit()

    async def delete_user(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def delete_snps(self) -> int:
        query = select(SNP)
        snps: list[SNP] = await self.fetch_all_rows(query)
        count: int = len(snps)
        for snp in snps:
            await self.session.delete(snp)
        await self.session.commit()
        return count
