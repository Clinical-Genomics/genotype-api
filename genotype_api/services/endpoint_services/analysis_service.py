"""Module for the analysis service."""

from pathlib import Path

from fastapi import UploadFile

from genotype_api.constants import FileExtension, Types
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

    async def get_analysis(self, analysis_id: int) -> AnalysisResponse:
        analysis: Analysis = await self.store.get_analysis_by_id(analysis_id=analysis_id)
        if not analysis:
            raise AnalysisNotFoundError
        return self._create_analysis_response(analysis)

    async def get_analyses(self, skip: int, limit: int) -> list[AnalysisResponse]:
        analyses: list[Analysis] = await self.store.get_analyses_with_skip_and_limit(
            skip=skip, limit=limit
        )
        if not analyses:
            raise AnalysisNotFoundError
        return [self._create_analysis_response(analysis) for analysis in analyses]

    async def get_upload_sequence_analyses(self, file: UploadFile) -> list[AnalysisResponse]:
        """
        Reading VCF file, creating and uploading sequence analyses and sample objects to the database.
        """
        file_name: Path = check_file(file_path=file.filename, extension=FileExtension.VCF)
        content = await file.file.read()
        sequence_analysis = SequenceAnalysis(
            vcf_file=content.decode("utf-8"), source=str(file_name)
        )
        analyses: list[Analysis] = list(sequence_analysis.generate_analyses())
        await self.store.check_analyses_objects(analyses=analyses, analysis_type=Types.SEQUENCE)
        await self.store.create_analyses_samples(analyses=analyses)
        for analysis in analyses:
            analysis: Analysis = await self.store.create_analysis(analysis=analysis)
            await self.store.refresh_sample_status(sample=analysis.sample)

        return [self._create_analysis_response(analysis) for analysis in analyses]

    async def delete_analysis(self, analysis_id: int) -> None:
        analysis: Analysis = await self.store.get_analysis_by_id(analysis_id=analysis_id)
        if not analysis:
            raise AnalysisNotFoundError
        await self.store.delete_analysis(analysis=analysis)
