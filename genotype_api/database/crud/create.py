import logging

from fastapi import HTTPException
from sqlmodel import Session
from sqlmodel.sql.expression import Select, SelectOfScalar

from genotype_api.database.models import Analysis, Plate, Sample, User, SNP
from genotype_api.dto.dto import UserCreate, PlateCreate
from genotype_api.dto.user import UserRequest

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

LOG = logging.getLogger(__name__)


def create_analysis(session: Session, analysis: Analysis) -> Analysis:
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def create_plate(session: Session, plate: PlateCreate) -> Plate:
    db_plate = Plate.from_orm(plate)
    db_plate.analyses = plate.analyses  # not sure why from_orm wont pick up the analyses
    session.add(db_plate)
    session.commit()
    session.refresh(db_plate)
    LOG.info(f"Creating plate with id {db_plate.plate_id}.")
    return db_plate


def create_sample(session: Session, sample: Sample) -> Sample:
    """Creates a sample in the database."""

    sample_in_db = session.get(Sample, sample.id)
    if sample_in_db:
        raise HTTPException(status_code=409, detail="Sample already registered")
    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


def create_analyses_samples(session: Session, analyses: list[Analysis]) -> list[Sample]:
    """creating samples in an analysis if not already in db."""
    return [
        create_sample(session=session, sample=Sample(id=analysis.sample_id))
        for analysis in analyses
        if not session.get(Sample, analysis.sample_id)
    ]


def create_user(session: Session, user: UserRequest):
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def create_snps(session: Session, snps: list[SNP]) -> list[SNP]:
    session.add_all(snps)
    session.commit()
    return snps
