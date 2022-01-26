"""Routes for the snps"""
from genotype_api.models import SNP, User
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, File
from genotype_api.database import get_session
from sqlmodel import Session, delete, select

from genotype_api.security import get_active_user

router = APIRouter()


@router.get("/", response_model=List[SNP])
def read_snps(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> List[SNP]:
    return session.exec(select(SNP).offset(skip).limit(limit)).all()


@router.post("/", response_model=List[SNP])
def upload_snps(
    snps_file: bytes = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    db_snps: List[SNP] = session.exec(select(SNP)).all()
    if db_snps:
        raise HTTPException(status_code=400, detail="SNPs already uploaded")
    snps = []
    content = snps_file.decode()
    header = ["id", "ref", "chrom", "pos"]
    for line in content.split("\n"):
        if len(line) <= 10:
            continue
        snp = SNP(**dict(zip(header, line.split())))
        session.add(snp)
        snps.append(snp)
    session.commit()
    return snps


@router.delete("/")
def delete_snps(
    session: Session = Depends(get_session), current_user: User = Depends(get_active_user)
):
    """Delete all SNPs"""

    result = session.exec(delete(SNP))
    session.commit()
    return {"message": f"all snps deleted ({result.rowcount} snps)"}
