"""Module to hold the snp service."""

from fastapi import UploadFile

from genotype_api.database.crud.create import create_snps
from genotype_api.database.crud.delete import delete_snps
from genotype_api.database.crud.read import get_snps_by_limit_and_skip, get_snps
from genotype_api.database.models import SNP
from genotype_api.dto.snp import SNPResponse
from genotype_api.exceptions import SNPExistsError
from genotype_api.services.snp_reader_service.snp_reader import SNPReaderService


class SNPService:

    def __init__(self, session):
        self.session = session

    @staticmethod
    def _get_snp_response(snp: SNP):
        return SNPResponse(ref=snp.ref, chrom=snp.chrom, pos=snp.pos, id=snp.id)

    def get_snps(self, skip: int, limit: int) -> list[SNPResponse]:
        snps: list[SNP] = get_snps_by_limit_and_skip(session=self.session, skip=skip, limit=limit)
        return [self._get_snp_response(snp) for snp in snps]

    def upload_snps(self, snps_file: UploadFile) -> list[SNPResponse]:
        existing_snps: list[SNP] = get_snps(self.session)
        if existing_snps:
            raise SNPExistsError
        snps: list[SNP] = SNPReaderService.read_snps_from_file(snps_file)
        new_snps: list[snps] = create_snps(session=self.session, snps=snps)
        return [self._get_snp_response(new_snp) for new_snp in new_snps]

    def delete_snps(self) -> int:
        result = delete_snps(self.session)
        return result.rowcount
