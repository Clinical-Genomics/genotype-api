"""Module for the analysis service."""

from pathlib import Path

from fastapi import UploadFile

from genotype_api.constants import Types, FileExtension
from genotype_api.database.models import Analysis


from genotype_api.dto.analysis import AnalysisResponse
from genotype_api.exceptions import AnalysisNotFoundError

from genotype_api.file_parsing.files import check_file
from genotype_api.file_parsing.vcf import SequenceAnalysis
from genotype_api.services.endpoint_services.base_service import BaseService


class AnalysisService(BaseService):
    """This service acts as a translational layer between the CRUD and the API."""

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
        analysis: Analysis = self.store.get_analysis_by_id(analysis_id=analysis_id)
        if not analysis:
            raise AnalysisNotFoundError
        return self._create_analysis_response(analysis)

    def get_analyses(self, skip: int, limit: int) -> list[AnalysisResponse]:
        analyses: list[Analysis] = self.store.get_analyses_with_skip_and_limit(
            skip=skip, limit=limit
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
        self.store.check_analyses_objects(analyses=analyses, analysis_type=Types.SEQUENCE)
        self.store.create_analyses_samples(analyses=analyses)
        for analysis in analyses:
            analysis: Analysis = self.store.create_analysis(analysis=analysis)
            self.store.refresh_sample_status(sample=analysis.sample)

        return [self._create_analysis_response(analysis) for analysis in analyses]

    def delete_analysis(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_by_id(analysis_id=analysis_id)
        if not analysis:
            raise AnalysisNotFoundError
        self.store.delete_analysis(analysis=analysis)
