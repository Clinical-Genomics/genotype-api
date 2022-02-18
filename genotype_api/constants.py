"""Constants used over the package"""
from enum import Enum
from pydantic import BaseModel


class TYPES(str, Enum):
    GENOTYPE = "genotype"
    SEQUENCE = "sequence"


class SEXES(str, Enum):
    MAIL = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class STATUS(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    CANCEL = "cancel"


CUTOFS = dict(max_nocalls=2, max_mismatch=4, min_matches=2)
