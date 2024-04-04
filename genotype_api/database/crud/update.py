import types

from pydantic import EmailStr
from sqlmodel import Session

from genotype_api.constants import Types
from genotype_api.database.crud.read import get_sample
from genotype_api.database.filter_models.plate_models import PlateSignOff
from genotype_api.database.filter_models.sample_models import SampleSexesUpdate
from genotype_api.database.models import Sample, Plate, User
from sqlmodel.sql.expression import Select, SelectOfScalar

from genotype_api.exceptions import SampleNotFoundError
from genotype_api.services.match_genotype_service.match_genotype import MatchGenotypeService

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


def refresh_sample_status(sample: Sample, session: Session) -> Sample:
    if len(sample.analyses) != 2:
        sample.status = None
    else:
        results = MatchGenotypeService.check_sample(sample=sample)
        sample.status = "fail" if "fail" in results.dict().values() else "pass"

    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


def update_sample_comment(session: Session, sample_id: str, comment: str) -> Sample:
    sample: Sample = get_sample(session=session, sample_id=sample_id)
    if not sample:
        raise SampleNotFoundError
    sample.comment = comment
    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


def update_sample_status(session: Session, sample_id: str, status: str | None) -> Sample:
    sample: Sample = get_sample(session=session, sample_id=sample_id)
    if not sample:
        raise SampleNotFoundError
    sample.status = status
    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


def refresh_plate(session: Session, plate: Plate) -> None:
    session.refresh(plate)


def update_plate_sign_off(session: Session, plate: Plate, plate_sign_off: PlateSignOff) -> Plate:
    plate.signed_by = plate_sign_off.user_id
    plate.signed_at = plate_sign_off.signed_at
    plate.method_document = plate_sign_off.method_document
    plate.method_version = plate_sign_off.method_version
    session.commit()
    session.refresh(plate)
    return plate


def update_sample_sex(session: Session, sexes_update: SampleSexesUpdate) -> Sample:
    sample: Sample = get_sample(session=session, sample_id=sexes_update.sample_id)
    if not sample:
        raise SampleNotFoundError
    sample.sex = sexes_update.sex
    for analysis in sample.analyses:
        if sexes_update.genotype_sex and analysis.type == Types.GENOTYPE:
            analysis.sex = sexes_update.genotype_sex
        elif sexes_update.sequence_sex and analysis.type == Types.SEQUENCE:
            analysis.sex = sexes_update.sequence_sex
        session.add(analysis)
    session.add(sample)
    session.commit()
    session.refresh(sample)
    sample: Sample = refresh_sample_status(session=session, sample=sample)
    return sample


def update_user_email(session: Session, user: User, email: EmailStr) -> User:
    user.email = email
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
