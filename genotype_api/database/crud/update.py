from pydantic import EmailStr


from genotype_api.constants import Types
from genotype_api.database.base_handler import BaseHandler
from genotype_api.database.filter_models.plate_models import PlateSignOff
from genotype_api.database.filter_models.sample_models import SampleSexesUpdate
from genotype_api.database.models import Sample, Plate, User
from genotype_api.exceptions import SampleNotFoundError
from genotype_api.services.match_genotype_service.match_genotype import MatchGenotypeService


class UpdateHandler(BaseHandler):

    def refresh_sample_status(
        self,
        sample: Sample,
    ) -> Sample:
        if len(sample.analyses) != 2:
            sample.status = None
        else:
            results = MatchGenotypeService.check_sample(sample=sample)
            sample.status = "fail" if "fail" in results.dict().values() else "pass"

        self.session.add(sample)
        self.session.commit()
        self.session.refresh(sample)
        return sample

    def update_sample_comment(self, sample_id: str, comment: str) -> Sample:
        sample: Sample = self.get_sample(sample_id=sample_id)
        if not sample:
            raise SampleNotFoundError
        sample.comment = comment
        self.session.add(sample)
        self.session.commit()
        self.session.refresh(sample)
        return sample

    def update_sample_status(self, sample_id: str, status: str | None) -> Sample:
        sample: Sample = self.get_sample(sample_id=sample_id)
        if not sample:
            raise SampleNotFoundError
        sample.status = status
        self.session.add(sample)
        self.session.commit()
        self.session.refresh(sample)
        return sample

    def refresh_plate(self, plate: Plate) -> None:
        self.session.refresh(plate)

    def update_plate_sign_off(self, plate: Plate, plate_sign_off: PlateSignOff) -> Plate:
        plate.signed_by = plate_sign_off.user_id
        plate.signed_at = plate_sign_off.signed_at
        plate.method_document = plate_sign_off.method_document
        plate.method_version = plate_sign_off.method_version
        self.session.commit()
        self.session.refresh(plate)
        return plate

    def update_sample_sex(self, sexes_update: SampleSexesUpdate) -> Sample:
        sample = (
            self.session.query(Sample).filter(Sample.id == sexes_update.sample_id).one_or_none()
        )
        if not sample:
            raise SampleNotFoundError
        sample.sex = sexes_update.sex
        for analysis in sample.analyses:
            if sexes_update.genotype_sex and analysis.type == Types.GENOTYPE:
                analysis.sex = sexes_update.genotype_sex
            elif sexes_update.sequence_sex and analysis.type == Types.SEQUENCE:
                analysis.sex = sexes_update.sequence_sex
            self.session.add(analysis)
        self.session.add(sample)
        self.session.commit()
        self.session.refresh(sample)
        sample = self.refresh_sample_status(sample)
        return sample

    def update_user_email(self, user: User, email: EmailStr) -> User:
        user.email = email
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
