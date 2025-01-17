"""Module for the match genotype services."""

from collections import Counter

from genotype_api.database.models import Analysis, Sample
from genotype_api.models import MatchCounts, MatchResult, SampleDetail
from genotype_api.services.match_genotype_service.utils import (
    check_sex,
    check_snps,
    compare_genotypes,
)


class MatchGenotypeService:
    @staticmethod
    def get_matches(analyses: list[Analysis], sample_analysis: Analysis) -> list[MatchResult]:
        if sample_analysis is None or sample_analysis.genotypes is None:
            return []

        match_results = []
        for genotype in analyses:
            if genotype is None or genotype.genotypes is None:
                continue
            genotype_pairs = zip(genotype.genotypes, sample_analysis.genotypes)
            results = dict(
                compare_genotypes(genotype_1, genotype_2)
                for genotype_1, genotype_2 in genotype_pairs
            )
            count = Counter([val for key, val in results.items()])
            if count.get("match", 0) + count.get("unknown", 0) > 40:
                match_results.append(
                    MatchResult(
                        sample_id=genotype.sample_id,
                        match_results=MatchCounts.parse_obj(count),
                    ),
                )
        return match_results

    @staticmethod
    def check_sample(sample: Sample) -> SampleDetail:
        """Check a sample for inconsistencies."""
        status = check_snps(
            genotype_analysis=sample.genotype_analysis,
            sequence_analysis=sample.sequence_analysis,
        )
        status.update(
            {
                "sex": check_sex(
                    sample_sex=sample.sex,
                    sequence_analysis=sample.sequence_analysis,
                    genotype_analysis=sample.genotype_analysis,
                )
            }
        )
        return SampleDetail(**status)
