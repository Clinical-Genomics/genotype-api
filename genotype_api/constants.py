"""Constants used over the package"""

from enum import StrEnum


class AnalysisTypes(StrEnum):
    GENOTYPE = "genotype"
    SEQUENCE = "sequence"


class Sexes(StrEnum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class Status(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    CANCEL = "cancel"


CUTOFS = dict(max_nocalls=15, max_mismatch=3, min_matches=35)
