"""Constants used over the package"""

import enum


class AnalysisTypes(enum.Enum):
    GENOTYPE: str = "genotype"
    SEQUENCE: str = "sequence"


class Sexes(enum.Enum):
    MALE: str = "male"
    FEMALE: str = "female"
    UNKNOWN: str = "unknown"


class Status(enum.Enum):
    PASS: str = "pass"
    FAIL: str = "fail"
    CANCEL: str = "cancel"


CUTOFS = dict(max_nocalls=15, max_mismatch=3, min_matches=35)
