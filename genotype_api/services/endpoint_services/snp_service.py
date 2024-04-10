"""Module to hold the snp service."""

from fastapi import UploadFile

from genotype_api.database.models import SNP

from genotype_api.dto.snp import SNPResponse
from genotype_api.exceptions import SNPExistsError
from genotype_api.services.endpoint_services.base_service import BaseService
from genotype_api.services.snp_reader_service.snp_reader import SNPReaderService


class SNPService(BaseService):

    @staticmethod
    def _get_snp_response(snp: SNP) -> SNPResponse:
        return SNPResponse(ref=snp.ref, chrom=snp.chrom, pos=snp.pos, id=snp.id)

    def get_snps(self, skip: int, limit: int) -> list[SNPResponse]:
        snps: list[SNP] = self.store.get_snps_by_limit_and_skip(skip=skip, limit=limit)
        return [self._get_snp_response(snp) for snp in snps]

    def upload_snps(self, snps_file: UploadFile) -> list[SNPResponse]:
        """Upload snps to the database, raises an error when SNPs already exist."""
        existing_snps: list[SNP] = self.store.get_snps()
        if existing_snps:
            raise SNPExistsError
        snps: list[SNP] = SNPReaderService.read_snps_from_file(snps_file)
        new_snps: list[SNP] = self.store.create_snps(snps=snps)
        return [self._get_snp_response(new_snp) for new_snp in new_snps]

    def delete_all_snps(self) -> int:
        result = self.store.delete_snps()
        return result.rowcount
