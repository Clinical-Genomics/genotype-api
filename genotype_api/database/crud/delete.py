import logging

from sqlalchemy import delete
from sqlmodel import Session
from sqlmodel.sql.expression import Select, SelectOfScalar

from genotype_api.database.models import Analysis, Plate, Sample, User, SNP

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

LOG = logging.getLogger(__name__)


def delete_analysis(session: Session, analysis: Analysis) -> None:
    session.delete(analysis)
    session.commit()


def delete_plate(session: Session, plate: Plate) -> None:
    session.delete(plate)
    session.commit()


def delete_sample(session: Session, sample: Sample) -> None:
    session.delete(sample)
    session.commit()


def delete_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()


def delete_snps(session) -> any:
    result = session.exec(delete(SNP))
    session.commit()
    return result
