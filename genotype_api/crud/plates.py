import logging
from typing import Optional
from genotype_api.models import Plate, PlateCreate
from sqlmodel import Session, select

LOG = logging.getLogger(__name__)


def get_plate(session: Session, plate_id: int) -> Plate:
    """Get plate"""

    statement = select(Plate).where(Plate.id == plate_id)
    return session.exec(statement).one()


def get_plate_by_plate_id(session: Session, plate_id: str) -> Optional[Plate]:
    statement = select(Plate).where(Plate.plate_id == plate_id)
    return session.exec(statement).first()


def create_plate(session: Session, plate: PlateCreate) -> Plate:
    db_plate = Plate.from_orm(plate)
    db_plate.analyses = plate.analyses  # not sure why from_orm wont pick up the analyses
    session.add(db_plate)
    session.commit()
    session.refresh(db_plate)
    LOG.info("Creating plate with id %s", db_plate.plate_id)
    return db_plate


def delete_plate(session: Session, plate_id: int) -> Optional[Plate]:
    db_plate: Plate = session.get(Plate, plate_id)
    if not db_plate:
        LOG.info("Could not find plate %s", plate_id)
        return None
    session.delete(db_plate)
    session.commit()
    LOG.info("Plate deleted")
    return db_plate
