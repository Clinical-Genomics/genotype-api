import logging

from sqlmodel import Session
from sqlmodel.sql.expression import Select, SelectOfScalar

from genotype_api.database.models import Analysis, Plate

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

LOG = logging.getLogger(__name__)


def delete_analysis(session: Session, analysis_id: int) -> Analysis:
    db_analysis = session.get(Analysis, analysis_id)
    session.delete(db_analysis)
    session.commit()
    return db_analysis


def delete_plate(session: Session, plate_id: int) -> Plate | None:
    db_plate: Plate = session.get(Plate, plate_id)
    if not db_plate:
        LOG.info(f"Could not find plate {plate_id}")
        return None
    session.delete(db_plate)
    session.commit()
    LOG.info("Plate deleted")
    return db_plate
