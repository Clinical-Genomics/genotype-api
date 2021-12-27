from typing import List

import genotype_api.models
from genotype_api.models import models
from sqlalchemy.orm import Session


def get_snps(db: Session) -> List[genotype_api.models.SNP]:
    return db.query(genotype_api.models.SNP).all()


def create_snp(db: Session, snp: genotype_api.models.SNP) -> genotype_api.models.SNP:
    db.add(snp)
    db.commit()
    db.refresh(snp)
    return snp


def delete_snp(db: Session, id: str) -> genotype_api.models.SNP:
    db_snp = db.query(genotype_api.models.SNP).filter(genotype_api.models.SNP.id == id).first()
    db.delete(db_snp)
    db.commit()
    return db_snp


def delete_all_snps(db: Session) -> None:
    db.query(genotype_api.models.SNP).delete()
    db.commit()
