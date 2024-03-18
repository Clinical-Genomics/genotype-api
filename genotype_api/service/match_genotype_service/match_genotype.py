"""Module for the match genotype service."""

from collections import Counter

from genotype_api.database.models import Analysis
from genotype_api.models import MatchResult, MatchCounts
from genotype_api.service.match_genotype_service.utils import compare_genotypes


class MatchGenotypeService:
    @staticmethod
    def get_matches(analyses: list[Analysis], sample_analysis: Analysis) -> list[MatchResult]:
        match_results = []
        for genotype in analyses:
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
