import logging
from sqlalchemy import delete


from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.models import Analysis, Plate, Sample, User, SNP

LOG = logging.getLogger(__name__)


class DeleteHandler(BaseHandler):

    def delete_analysis(self, analysis: Analysis) -> None:
        self.session.delete(analysis)
        self.session.commit()

    def delete_plate(self, plate: Plate) -> None:
        self.session.delete(plate)
        self.session.commit()

    def delete_sample(self, sample: Sample) -> None:
        self.session.delete(sample)
        self.session.commit()

    def delete_user(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()

    def delete_snps(self) -> int:
        snps: list[SNP] = self._get_query(SNP).all()
        count: int = len(snps)
        for snp in snps:
            self.session.delete(snp)
        self.session.commit()
        return count
