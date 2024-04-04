"""Genotype specific exceptions"""


class SexConflictError(Exception):
    pass


class UnknownAllelesError(Exception):
    pass


class InsufficientAnalysesError(Exception):
    pass


class PlateExistsError(Exception):
    pass


class PlateNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserArchiveError(Exception):
    pass


class UserExistsError(Exception):
    pass


class AnalysisNotFoundError(Exception):
    pass


class SampleNotFoundError(Exception):
    pass


class SampleExistsError(Exception):
    pass


class SNPExistsError(Exception):
    pass
