"""Genotype specific exceptions"""


class SexConflictError(Exception):
    pass


class UnknownAllelesError(Exception):
    pass


class InsufficientAnalysesError(Exception):
    pass


class PlateExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserArchiveError(Exception):
    pass


class UserExistsError(Exception):
    pass
