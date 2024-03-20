"""Module to holds the plate service."""

from sqlmodel import Session


class PlateService:

    def __init__(self, session: Session):
        self.session: Session = session
