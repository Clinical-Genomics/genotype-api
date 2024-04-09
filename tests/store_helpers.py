"""Module that holds the store helper to be used to setup the testing environment."""

from genotype_api.database.models import Sample, Analysis, User, SNP, Plate, Genotype
from genotype_api.database.store import Store


class StoreHelpers:
    """Class to hold helper functions to setup the store testing environment."""

    @classmethod
    def add_entity(cls, store: Store, entity: Sample | Analysis | SNP | Plate | User | Genotype):
        store.session.add(entity)

    def ensure_sample(self, store: Store, sample: Sample, analyses: list[Analysis] = None):
        """Add a sample to the store. Ensure its analyses are present."""
        if analyses:
            for analysis in analyses:
                if not store.get_analysis_by_id(analysis.id):
                    self.add_entity(store=store, entity=analysis)
        self.add_entity(store=store, entity=sample)
        store.session.commit()

    def ensure_snp(self, store: Store, snp: SNP):
        self.add_entity(store=store, entity=snp)
        store.session.commit()

    def ensure_plate(
        self, store: Store, plate: Plate, analyses: list[Analysis] = None, user: User = None
    ):
        """Add a plate to the store ensure the associated user and analyses are present."""
        if user and not store.get_user_by_email(user.email):
            self.add_entity(store=store, entity=user)
        if analyses:
            for analysis in analyses:
                if not store.get_analysis_by_id(analysis.id):
                    self.add_entity(store=store, entity=analysis)
        self.add_entity(store=store, entity=plate)
        store.session.commit()

    def ensure_user(self, store: Store, user: User, plates: list[Plate] = None):
        """Add a user to the store and ensure the associated plates are present."""
        if plates:
            for plate in plates:
                if not store.get_plate_by_id(plate.id):
                    self.add_entity(store=store, entity=plate)
        self.add_entity(store=store, entity=user)
        store.session.commit()

    def ensure_analysis(
        self,
        store: Store,
        analysis: Analysis,
        sample: Sample = None,
        plate: Plate = None,
        genotypes: list[Genotype] = None,
    ):
        """Add an analysis to the store and ensure the associated sample, plate and genotypes are present."""
        if sample and not store.get_sample(sample.id):
            self.add_entity(store=store, entity=sample)
        if plate and not store.get_plate_by_id(plate.id):
            self.add_entity(store=store, entity=plate)
        if genotypes:
            for genotype in genotypes:
                if not store.get_genotype_by_id(genotype.id):
                    self.add_entity(store=store, entity=genotype)
        self.add_entity(store=store, entity=analysis)
        store.session.commit()

    def ensure_genotype(self, store: Store, genotype: Genotype, analysis: Analysis = None):
        """Add a genotype to the database and ensure the associated analysis is present."""
        if analysis and not store.get_analysis_by_id(analysis.id):
            self.add_entity(store=store, entity=analysis)
        self.add_entity(store=store, entity=genotype)
        store.session.commit()
