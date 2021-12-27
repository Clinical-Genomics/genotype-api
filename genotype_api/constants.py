"""Constants used over the package"""
from enum import Enum


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
