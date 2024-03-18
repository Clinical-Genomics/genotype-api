from sqlmodel import Session


from genotype_api.database.crud.read import get_sample
from genotype_api.database.filter_models.plate_models import PlateSignOff
from genotype_api.match import check_sample
from genotype_api.database.models import Sample, Plate
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


def refresh_sample_status(sample: Sample, session: Session) -> Sample:
    if len(sample.analyses) != 2:
        sample.status = None
    else:
        results = check_sample(sample=sample)
        sample.status = "fail" if "fail" in results.dict().values() else "pass"

    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


def update_sample_comment(session: Session, sample_id: str, comment: str) -> Sample:
    sample: Sample = get_sample(session=session, sample_id=sample_id)
    sample.comment = comment
    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


def update_sample_status(session: Session, sample_id: str, status: str | None) -> Sample:
    sample: Sample = get_sample(session=session, sample_id=sample_id)
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
