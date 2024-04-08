"""Module that holds the store helper to be used to setup the testing environment."""

from genotype_api.database.models import Sample, Analysis, User, SNP, Plate, Genotype
from genotype_api.database.store import Store


class StoreHelpers:
    """Class to hold helper functions that needs to be used all over."""

    def __init__(self, store: Store):
        self.store: Store = store

    def add_entity(self, entity: Sample | Analysis | SNP | Plate | User | Genotype):
        self.store.session.add(entity)
        self.store.session.commit()

    def ensure_sample(self, sample: Sample, analyses: list[Analysis] = None):
        """Add a sample to the store. Ensure its analyses are present."""
        if analyses:
            for analysis in analyses:
                if not self.store.get_analysis_by_id(analysis.id):
                    self.add_entity(entity=analysis)
        self.add_entity(entity=sample)

    def ensure_snp(self, snp: SNP):
        self.add_entity(entity=snp)

    def ensure_plate(self, plate: Plate, analyses: list[Analysis] = None, user: User = None):
        """Add a plate to the store ensure the associated user and analyses are present."""
        if user:
            if not self.store.get_user_by_email(user.email):
                self.add_entity(user)
        if analyses:
            for analysis in analyses:
                if not self.store.get_analysis_by_id(analysis.id):
                    self.add_entity(analysis)
        self.add_entity(plate)

    def ensure_user(self, user: User, plates: list[Plate] = None):
        """Add a user to the store and ensure the associated plates are present."""
        if plates:
            for plate in plates:
                if not self.store.get_plate_by_id(plate.id):
                    self.add_entity(entity=plate)
        self.add_entity(user)

    def ensure_analysis(
        self, analysis: Analysis, sample: Sample, plate: Plate, genotypes: list[Genotype]
    ):
        """Add an analysis to the store and ensure the associated sample, plate and genotypes are present."""
        if sample:
            if not self.store.get_sample(sample.id):
                self.add_entity(sample)
        if plate:
            if not self.store.get_plate_by_id(plate.id):
                self.add_entity(plate)
        if genotypes:
            for genotype in genotypes:
                if not self.store.get_genotype_by_id(genotype.id):
                    self.add_entity(genotype)
        self.add_entity(analysis)

    def ensure_genotype(self, genotype: Genotype, analysis: Analysis = None):
        """Add a genotype to the database and ensure the associated analysis is present."""
        if analysis and not self.store.get_analysis_by_id(analysis.id):
            self.add_entity(analysis)
        self.add_entity(genotype)
