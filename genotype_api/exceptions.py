"""Genotype specific exceptions"""


class SexConflictError(Exception):
    pass


class UnknownAllelesError(Exception):
    pass


class InsufficientAnalysesError(Exception):
    pass
