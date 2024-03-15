"""Constants used over the package"""

from enum import Enum


class AnalysisTypes(Enum):
    GENOTYPE = "genotype"
    SEQUENCE = "sequence"


class Sexes(Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class Status(Enum):
    PASS = "pass"
    FAIL = "fail"
    CANCEL = "cancel"


CUTOFS = dict(max_nocalls=15, max_mismatch=3, min_matches=35)
