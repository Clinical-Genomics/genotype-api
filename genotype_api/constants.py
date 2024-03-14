"""Constants used over the package"""

import enum


class TYPES(str, enum.Enum):
    GENOTYPE = "genotype"
    SEQUENCE = "sequence"


class SEXES(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class STATUS(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    CANCEL = "cancel"


CUTOFS = dict(max_nocalls=15, max_mismatch=3, min_matches=35)
