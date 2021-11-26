"""Routes for the snps"""

from pathlib import Path
from typing import List

import genotype_api.crud.snps
from fastapi import APIRouter, Depends, File, HTTPException
from genotype_api import crud
from genotype_api.database import get_session
from genotype_api.models import SNP as DB_SNP
from genotype_api.schemas.snps import SNP
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[SNP])
def read_snps(db: Session = Depends(get_session)):
    """Return all snpns."""
    snps = genotype_api.crud.snps.get_snps(db)

    return snps


@router.post("/", response_model=List[SNP])
def upload_snps(snps_file: bytes = File(...), db: Session = Depends(get_session)):
    db_snps = genotype_api.crud.snps.get_snps(db=db)
    if db_snps:
        raise HTTPException(status_code=400, detail="SNPs already uploaded")
    snps = []
    content = snps_file.decode()
    header = ["id", "ref", "chrom", "pos"]
    for line in content.split("\n"):
        if not len(line) > 10:
            continue
        snp = SNP(**dict(zip(header, line.split())))
        db_snp = DB_SNP(**snp.dict())
        snps.append(genotype_api.crud.snps.create_snp(db=db, snp=db_snp))

    return snps


@router.delete("/")
def delete_snps(db: Session = Depends(get_session)):
    genotype_api.crud.snps.delete_all_snps(db=db)
    return {"message": "all snps deleted"}
