from typing import List

from genotype_api import models
from sqlalchemy.orm import Session


def get_snps(db: Session) -> List[models.SNP]:
    return db.query(models.SNP).all()


def create_snp(db: Session, snp: models.SNP) -> models.SNP:
    db.add(snp)
    db.commit()
    db.refresh(snp)
    return snp


def delete_snp(db: Session, id: str) -> models.SNP:
    db_snp = db.query(models.SNP).filter(models.SNP.id == id).first()
    db.delete(db_snp)
    db.commit()
    return db_snp


def delete_all_snps(db: Session) -> None:
    db.query(models.SNP).delete()
    db.commit()
