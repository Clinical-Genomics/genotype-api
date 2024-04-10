import logging


from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.models import Analysis, Plate, Sample, User, SNP, Genotype
from genotype_api.dto.user import UserRequest
from genotype_api.exceptions import SampleExistsError

LOG = logging.getLogger(__name__)


class CreateHandler(BaseHandler):

    def create_analysis(self, analysis: Analysis) -> Analysis:
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)
        return analysis

    def create_plate(self, plate: Plate) -> Plate:
        self.session.add(plate)
        self.session.commit()
        self.session.refresh(plate)
        LOG.info(f"Creating plate with id {plate.plate_id}.")
        return plate

    def create_sample(self, sample: Sample) -> Sample:
        """Creates a sample in the database."""
        sample_in_db = self.session.query(Sample).filter(Sample.id == sample.id).one_or_none()
        if sample_in_db:
            raise SampleExistsError
        self.session.add(sample)
        self.session.commit()
        self.session.refresh(sample)
        return sample

    def create_analyses_samples(self, analyses: list[Analysis]) -> list[Sample]:
        """creating samples in an analysis if not already in db."""
        return [
            self.create_sample(sample=Sample(id=analysis.sample_id))
            for analysis in analyses
            if not self.session.query(Sample).filter(Sample.id == analysis.sample_id).one_or_none()
        ]

    def create_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def create_snps(self, snps: list[SNP]) -> list[SNP]:
        self.session.add_all(snps)
        self.session.commit()
        return snps

    def create_genotype(self, genotype: Genotype) -> Genotype:
        self.session.add(genotype)
        self.session.commit()
        return genotype
