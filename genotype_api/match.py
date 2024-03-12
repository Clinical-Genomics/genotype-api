"""Code for matching entities in the database"""

import logging
from genotype_api.models import (
    SampleDetail,
)
from genotype_api.database.models import Sample, check_snps, check_sex

log = logging.getLogger(__name__)


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
