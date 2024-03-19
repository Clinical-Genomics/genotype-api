"""Utils functions for the match genotype services."""

from collections import Counter

from genotype_api.constants import CUTOFS, SEXES
from genotype_api.database import models


def compare_genotypes(genotype_1: models.Genotype, genotype_2: models.Genotype) -> tuple[str, str]:
    """Compare two genotypes if they have the same alleles."""

    if "0" in genotype_1.alleles or "0" in genotype_2.alleles:
        return genotype_1.rsnumber, "unknown"
    elif genotype_1.alleles == genotype_2.alleles:
        return genotype_1.rsnumber, "match"
    else:
        return genotype_1.rsnumber, "mismatch"


def check_sex(sample_sex, genotype_analysis, sequence_analysis):
    """Check if any source disagrees on the sex"""
    if not sample_sex or genotype_analysis.sex == SEXES.UNKNOWN:
        return "fail"
    sexes = {genotype_analysis.sex, sequence_analysis.sex, sample_sex}
    if {SEXES.MALE, SEXES.FEMALE}.issubset(sexes):
        return "fail"
    return "pass"


def check_snps(genotype_analysis, sequence_analysis):
    genotype_pairs = zip(genotype_analysis.genotypes, sequence_analysis.genotypes)
    results = dict(
        compare_genotypes(genotype_1, genotype_2) for genotype_1, genotype_2 in genotype_pairs
    )
    count = Counter([val for key, val in results.items()])
    unknown = count.get("unknown", 0)
    matches = count.get("match", 0)
    mismatches = count.get("mismatch", 0)
    snps = (
        "pass"
        if all([matches >= CUTOFS.get("min_matches") and mismatches <= CUTOFS.get("max_mismatch")])
        else "fail"
    )
    nocalls = "pass" if unknown <= CUTOFS.get("max_nocalls") else "fail"
    failed_snps = [key for key, val in results.items() if val == "mismatch"]

    return {
        "unknown": unknown,
        "matches": matches,
        "mismatches": mismatches,
        "snps": snps,
        "nocalls": nocalls,
        "failed_snps": failed_snps,
    }
