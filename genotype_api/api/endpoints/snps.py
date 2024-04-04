"""Routes for the snps"""

from fastapi import APIRouter, Depends, Query, UploadFile
from sqlalchemy.orm import Session

from starlette.responses import JSONResponse


from genotype_api.database.models import SNP, User


from genotype_api.database.store import Store, get_store
from genotype_api.dto.snp import SNPResponse
from genotype_api.exceptions import SNPExistsError
from genotype_api.security import get_active_user

from genotype_api.services.endpoint_services.snp_service import SNPService


router = APIRouter()


def get_snp_service(store: Store = Depends(get_store)) -> SNPService:
    return SNPService(store)


@router.get("/", response_model=list[SNPResponse])
def read_snps(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    snp_service: SNPService = Depends(get_snp_service),
    current_user: User = Depends(get_active_user),
):
    return snp_service.get_snps(skip=skip, limit=limit)


@router.post("/", response_model=list[SNP])
async def upload_snps(
    snps_file: UploadFile,
    snp_service: SNPService = Depends(get_snp_service),
    current_user: User = Depends(get_active_user),
):
    try:
        return snp_service.upload_snps(snps_file)
    except SNPExistsError:
        return JSONResponse(status_code=400, content="SNPs already uploaded")


@router.delete("/")
def delete_snps(
    snp_service: SNPService = Depends(get_snp_service),
    current_user: User = Depends(get_active_user),
):
    """Delete all SNPs"""

    result = snp_service.delete_all_snps()
    return {"message": f"all snps deleted ({result} snps)"}
