"""This module holds the SNP reader server."""

from fastapi.datastructures import UploadFile

from genotype_api.database.models import SNP

SNP_HEADER = ["id", "ref", "chrom", "pos"]


class SNPReaderService:
    @staticmethod
    def read_snps_from_file(snps_file: UploadFile) -> list[SNP]:
        snps: list[SNP] = []
        content = snps_file.read()
        header = SNP_HEADER
        for line in content.decode().split("\n"):
            if len(line) <= 10:
                continue
            snp = SNP(**dict(zip(header, line.split())))
            snps.append(snp)
        return snps
