"""Constants used over the package"""

from enum import StrEnum


class TYPES(StrEnum):
    GENOTYPE = "genotype"
    SEQUENCE = "sequence"


class SEXES(StrEnum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class STATUS(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    CANCEL = "cancel"


CUTOFS = dict(max_nocalls=15, max_mismatch=3, min_matches=35)
