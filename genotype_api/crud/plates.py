import logging
from typing import List, Optional

from genotype_api import models
from sqlalchemy.orm import Session

LOG = logging.getLogger(__name__)


def get_plates(db: Session, skip: int = 0, limit: int = 100) -> List[models.Plate]:
    return db.query(models.Plate).offset(skip).limit(limit).all()


def get_plate(db: Session, plate_id: int) -> Optional[models.Plate]:
    return db.query(models.Plate).filter(models.Plate.id == plate_id).first()


def get_plate_by_plate_id(db: Session, plate_id: str) -> Optional[models.Plate]:
    return db.query(models.Plate).filter(models.Plate.plate_id == plate_id).first()


def create_plate(db: Session, plate: models.Plate) -> models.Plate:
    LOG.info("Creating plate with id %s", plate.plate_id)
    db.add(plate)
    db.commit()
    db.refresh(plate)
    return plate


def delete_plate(db: Session, plate_id: int) -> Optional[models.Plate]:
    db_plate = get_plate(db=db, plate_id=plate_id)
    if not db_plate:
        LOG.info("Could not find plate %s", plate_id)
        return None
    db.delete(db_plate)
    db.commit()
    LOG.info("Plate deleted")
    return db_plate
