"""Utils functions for the match genotype service."""

from genotype_api.database.models import Genotype


def compare_genotypes(genotype_1: Genotype, genotype_2: Genotype) -> tuple[str, str]:
    """Compare two genotypes if they have the same alleles."""

    if "0" in genotype_1.alleles or "0" in genotype_2.alleles:
        return genotype_1.rsnumber, "unknown"
    elif genotype_1.alleles == genotype_2.alleles:
        return genotype_1.rsnumber, "match"
    else:
        return genotype_1.rsnumber, "mismatch"
