"""Module to holds the plate service."""

import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from pydantic import EmailStr

from genotype_api.constants import Types
from genotype_api.database.filter_models.plate_models import PlateOrderParams, PlateSignOff
from genotype_api.database.models import Analysis, Plate, Sample, User
from genotype_api.dto.plate import AnalysisOnPlate, PlateResponse, SampleStatus, UserOnPlate
from genotype_api.exceptions import PlateExistsError, PlateNotFoundError, UserNotFoundError
from genotype_api.file_parsing.excel import GenotypeAnalysis
from genotype_api.file_parsing.files import check_file
from genotype_api.services.endpoint_services.base_service import BaseService


class PlateService(BaseService):

    @staticmethod
    def _get_analyses_on_plate(plate: Plate) -> list[AnalysisOnPlate] | None:
        analyses_response: list[AnalysisOnPlate] = []
        for analysis in plate.analyses:
            if analysis:
                sample_status = SampleStatus(
                    status=analysis.sample.status, comment=analysis.sample.comment
                )
                analysis_response = AnalysisOnPlate(
                    type=analysis.type,
                    source=analysis.source,
                    sex=analysis.sex,
                    created_at=analysis.created_at,
                    sample_id=analysis.sample_id,
                    plate_id=analysis.plate_id,
                    id=analysis.id,
                    sample=sample_status,
                )
                analyses_response.append(analysis_response)
        return analyses_response if analyses_response else None

    async def _get_plate_user(self, plate: Plate) -> UserOnPlate | None:
        if plate.signed_by:
            user: User = await self.store.get_user_by_id(user_id=plate.signed_by)
            return UserOnPlate(email=user.email, name=user.name, id=user.id)
        return None

    async def _create_plate_response(self, plate: Plate) -> PlateResponse:
        analyses_response: list[AnalysisOnPlate] = self._get_analyses_on_plate(plate)
        user: UserOnPlate = await self._get_plate_user(plate)
        return PlateResponse(
            created_at=plate.created_at,
            plate_id=plate.plate_id,
            signed_by=plate.signed_by,
            signed_at=plate.signed_at,
            method_document=plate.method_document,
            method_version=plate.method_version,
            id=plate.id,
            user=user,
            analyses=analyses_response,
        )

    @staticmethod
    def _get_plate_id_from_file(file_name: Path) -> str:
        # Get the plate id from the standardized name of the plate
        return file_name.name.split("_", 1)[0]

    async def upload_plate(self, file: UploadFile) -> None:
        file_name: Path = check_file(file_path=file.filename, extension=".xlsx")
        plate_id: str = self._get_plate_id_from_file(file_name)
        db_plate = await self.store.get_plate_by_plate_id(plate_id)
        if db_plate:
            raise PlateExistsError

        excel_parser = GenotypeAnalysis(
            excel_file=BytesIO(file.file.read()),
            file_name=str(file_name),
            include_key="-CG-",
        )

        plate_obj = Plate(plate_id=plate_id)
        plate: Plate = await self.store.create_plate(plate=plate_obj)
        new_plate: Plate = await self.store.get_plate_by_plate_id(plate_id=plate_id)
        analyses: list[Analysis] = list(excel_parser.generate_analyses(plate_id=new_plate.id))
        await self.store.check_analyses_objects(analyses=analyses, analysis_type=Types.GENOTYPE)
        await self.store.create_analyses_samples(analyses=analyses)
        for analysis in analyses:
            await self.store.create_analysis(analysis=analysis)
        plate_obj.analyses = analyses
        for analysis in analyses:
            sample: Sample = await self.store.get_sample_by_id(sample_id=analysis.sample_id)
            await self.store.refresh_sample_status(sample=sample)
        await self.store.refresh_plate(plate=plate)

    async def update_plate_sign_off(
        self, plate_id: int, user_email: EmailStr, method_document: str, method_version: str
    ) -> PlateResponse:
        plate: Plate = await self.store.get_plate_by_id(plate_id=plate_id)
        if not plate:
            raise PlateNotFoundError
        user: User = await self.store.get_user_by_email(email=user_email)
        if not user:
            raise UserNotFoundError
        plate_sign_off = PlateSignOff(
            user_id=user.id,
            signed_at=datetime.now(),
            method_document=method_document,
            method_version=method_version,
        )
        await self.store.update_plate_sign_off(plate=plate, plate_sign_off=plate_sign_off)
        return await self._create_plate_response(plate)

    async def get_plate(self, plate_id: int) -> PlateResponse:
        plate = await self.store.get_plate_by_id(plate_id)

        if not plate:
            raise PlateNotFoundError

        return await self._create_plate_response(plate)

    async def get_plates(self, order_params: PlateOrderParams) -> list[PlateResponse]:
        plates: list[Plate] = await self.store.get_ordered_plates(order_params=order_params)
        if not plates:
            raise PlateNotFoundError
        return [await self._create_plate_response(plate) for plate in plates]

    async def delete_plate(self, plate_id) -> list[int]:
        """Delete a plate with the given plate id and return associated analysis ids."""
        plate = await self.store.get_plate_by_id(plate_id=plate_id)
        if not plate:
            raise PlateNotFoundError
        analyses: list[Analysis] = await self.store.get_analyses_by_plate_id(plate_id=plate_id)
        analysis_ids: list[int] = [analyse.id for analyse in analyses]
        for analysis in analyses:
            await self.store.delete_analysis(analysis=analysis)
        await self.store.delete_plate(plate=plate)
        return analysis_ids
