"""Module for the analysis service."""

from sqlmodel import Session

from genotype_api.database.crud.read import get_analysis_by_id
from genotype_api.database.models import Analysis
from genotype_api.dto.analysis import AnalysisWithGenotypeResponse


class AnalysisService:
    """This service acts as a translational layer between the crud and the api."""

    def __init__(self, session: Session):
        self.session: Session = session

    def get_analysis_with_genotype_response(self, analysis_id: int) -> AnalysisWithGenotypeResponse:
        analysis: Analysis = get_analysis_by_id(session=self.session, analysis_id=analysis_id)
        return AnalysisWithGenotypeResponse(**analysis.dict())
