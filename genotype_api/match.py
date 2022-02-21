"""Code for matching entities in the database"""

import logging
from collections import Counter, namedtuple
from typing import Dict, Literal, Optional

from genotype_api.constants import CUTOFS, SEXES
from genotype_api.models import Sample, Analysis, Genotype

log = logging.getLogger(__name__)
Result = namedtuple("Result", ["match", "mismatch", "unknown"])


def compare_genotypes(genotype_1: Genotype, genotype_2: Genotype) -> str:
    """Compare two genotypes if they have the same alleles."""

    if "0" in genotype_1.alleles or "0" in genotype_2.alleles:
        return "unknown"
    elif genotype_1.alleles == genotype_2.alleles:
        return "match"
    else:
        return "mismatch"


def check_sex(
    sex_1: Optional[str], sex_2: Optional[str], sex_3: Optional[str]
) -> Optional[Literal["fail", "pass"]]:
    """Compare three sex strings"""

    if sex_1 in ["unknown", None]:
        return "fail"
    if not sex_1 == sex_2 == sex_3:
        return "fail"
    return "pass"


def check_snps(analysis_1: Analysis, analysis_2: Analysis) -> Optional[Literal["fail", "pass"]]:
    genotype_pairs = zip(analysis_1.genotypes, analysis_2.genotypes)
    results = (
        compare_genotypes(genotype_1, genotype_2) for genotype_1, genotype_2 in genotype_pairs
    )
    count = Counter(results)
    enough_matches = count.get("match", 0) >= CUTOFS.get("min_matches")
    ok_mismatches = count.get("mismatch", 0) <= CUTOFS.get("max_mismatch")
    return "pass" if enough_matches and ok_mismatches else "fail"


def score_no_calls(genotype_analysis: Analysis) -> Optional[Literal["fail", "pass"]]:
    """score no calls."""
    calls = genotype_analysis.check_no_calls()
    return "fail" if calls["unknown"] >= CUTOFS.get("max_nocalls") else "pass"


def check_sample(sample: Sample):
    """Check a sample for inconsistencies."""

    assert len(sample.analyses) == 2, "must load both types of analyses"
    return dict(
        sex=check_sex(
            sex_1=sample.sex,
            sex_2=sample.genotype_analysis.sex,
            sex_3=sample.sequence_analysis.sex,
        ),
        compare=check_snps(
            analysis_1=sample.genotype_analysis,
            analysis_2=sample.sequence_analysis,
        ),
        nocalls=score_no_calls(genotype_analysis=sample.genotype_analysis),
    )
