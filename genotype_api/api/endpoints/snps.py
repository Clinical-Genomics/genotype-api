"""Routes for the snps"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlmodel import Session, delete, select
from sqlmodel.sql.expression import Select, SelectOfScalar

from genotype_api.database.models import SNP, User
from genotype_api.database.session_handler import get_session
from genotype_api.security import get_active_user

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

router = APIRouter()


@router.get("/", response_model=list[SNP])
def read_snps(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> list[SNP]:
    return session.exec(select(SNP).offset(skip).limit(limit)).all()


@router.post("/", response_model=list[SNP])
async def upload_snps(
    snps_file: UploadFile,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    db_snps: list[SNP] = session.exec(select(SNP)).all()
    if db_snps:
        raise HTTPException(status_code=400, detail="SNPs already uploaded")
    snps = []
    content = await snps_file.read()

    header = ["id", "ref", "chrom", "pos"]
    for line in content.decode().split("\n"):
        if len(line) <= 10:
            continue
        snp = SNP(**dict(zip(header, line.split())))
        session.add(snp)
        snps.append(snp)
    session.commit()
    return snps


@router.delete("/")
def delete_snps(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Delete all SNPs"""

    result = session.exec(delete(SNP))
    session.commit()
    return {"message": f"all snps deleted ({result.rowcount} snps)"}
