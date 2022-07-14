"""Constants used over the package"""
from enum import Enum
from pydantic import BaseModel


class TYPES(str, Enum):
    GENOTYPE = "genotype"
    SEQUENCE = "sequence"


class SEXES(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class STATUS(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    CANCEL = "cancel"


CUTOFS = dict(max_nocalls=15, max_mismatch=3, min_matches=35)
