"""Module for the analysis service."""

from pathlib import Path

from fastapi import UploadFile
from sqlmodel import Session

from genotype_api.constants import Types, FileExtension
from genotype_api.database.crud.create import create_analyses_samples, create_analysis
from genotype_api.database.crud.delete import delete_analysis
from genotype_api.database.crud.read import (
    get_analysis_by_id,
    get_analyses_with_skip_and_limit,
    check_analyses_objects,
)
from genotype_api.database.crud.update import refresh_sample_status
from genotype_api.database.models import Analysis

from genotype_api.dto.analysis import AnalysisResponse
from genotype_api.exceptions import AnalysisNotFoundError

from genotype_api.file_parsing.files import check_file
from genotype_api.file_parsing.vcf import SequenceAnalysis


class AnalysisService:
    """This service acts as a translational layer between the CRUD and the API."""

    def __init__(self, session: Session):
        self.session: Session = session

    @staticmethod
    def _create_analysis_response(analysis: Analysis) -> AnalysisResponse:
        return AnalysisResponse(
            type=analysis.type,
            source=analysis.source,
            sex=analysis.sex,
            created_at=analysis.created_at,
            sample_id=analysis.sample_id,
            plate_id=analysis.plate_id,
            id=analysis.id,
            genotypes=analysis.genotypes,
        )

    def get_analysis(self, analysis_id: int) -> AnalysisResponse:
        analysis: Analysis = get_analysis_by_id(session=self.session, analysis_id=analysis_id)
        if not analysis:
            raise AnalysisNotFoundError
        return self._create_analysis_response(analysis)

    def get_analyses(self, skip: int, limit: int) -> list[AnalysisResponse]:
        analyses: list[Analysis] = get_analyses_with_skip_and_limit(
            session=self.session, skip=skip, limit=limit
        )
        if not analyses:
            raise AnalysisNotFoundError
        return [self._create_analysis_response(analysis) for analysis in analyses]

    def get_upload_sequence_analyses(self, file: UploadFile) -> list[AnalysisResponse]:
        """
        Reading VCF file, creating and uploading sequence analyses and sample objects to the database.
        """
        file_name: Path = check_file(file_path=file.filename, extension=FileExtension.VCF)
        content = file.file.read().decode("utf-8")
        sequence_analysis = SequenceAnalysis(vcf_file=content, source=str(file_name))
        analyses: list[Analysis] = list(sequence_analysis.generate_analyses())
        check_analyses_objects(
            session=self.session, analyses=analyses, analysis_type=Types.SEQUENCE
        )
        create_analyses_samples(session=self.session, analyses=analyses)
        for analysis in analyses:
            analysis: Analysis = create_analysis(session=self.session, analysis=analysis)
            refresh_sample_status(session=self.session, sample=analysis.sample)

        return [self._create_analysis_response(analysis) for analysis in analyses]

    def delete_analysis(self, analysis_id: int) -> None:
        analysis: Analysis = get_analysis_by_id(session=self.session, analysis_id=analysis_id)
        if not analysis:
            raise AnalysisNotFoundError
        delete_analysis(session=self.session, analysis=analysis)
