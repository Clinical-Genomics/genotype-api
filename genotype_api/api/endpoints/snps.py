"""Routes for the snps"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlmodel import Session
from sqlmodel.sql.expression import Select, SelectOfScalar

from genotype_api.database.crud.create import create_snps
from genotype_api.database.crud.read import get_snps, get_snps_by_limit_and_skip
from genotype_api.database.models import SNP, User
from genotype_api.database.crud import delete
from genotype_api.database.session_handler import get_session
from genotype_api.security import get_active_user
from genotype_api.services.snp_reader.snp_reader import SNPReaderService

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
    return get_snps_by_limit_and_skip(session=session, skip=skip, limit=limit)


@router.post("/", response_model=list[SNP])
async def upload_snps(
    snps_file: UploadFile,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    existing_snps: list[SNP] = get_snps(session)
    if existing_snps:
        raise HTTPException(status_code=400, detail="SNPs already uploaded")
    snps: list[SNP] = SNPReaderService.read_snps_from_file(snps_file)
    new_snps: list[snps] = create_snps(session=session, snps=snps)
    return new_snps


@router.delete("/")
def delete_snps(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Delete all SNPs"""

    result = delete.delete_snps(session)
    return {"message": f"all snps deleted ({result.rowcount} snps)"}
