from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Body, File, UploadFile, Depends, status

from app.utils.session import create_session
from app.models.enums import DiseaseTypeEnum
from app.schemas.user import UserOutputSchema
from app.services.auth import AuthServices
from app.schemas.diagnosis import (
    DiagnosisOutputSchema,
    MobileDiagnosisInputSchema,
    UploadedFileSchema,
)
from app.services.diagnosis import DiagnosisServices, FileServices


router = APIRouter(prefix="/diagnosis", tags=["Diagnosis"])


@router.post(
    "/upload-image",
    response_model=UploadedFileSchema,
    status_code=status.HTTP_201_CREATED,
    description="Uploads an image file to the server.",
)
async def upload_image(
    db: Session = Depends(create_session),
    file: UploadFile = File(...),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
) -> UserOutputSchema:
    """
    Uploads an image file to the server.

    Args:
        db (Session): The database session.
        file (UploadFile): The image file to upload.
        current_user (UserOutputSchema): The current user performing the upload.

    Returns:
        UploadedFileSchema: The schema representing the uploaded file.
    """
    return FileServices.upload_image(db, file, current_user.id)


@router.post(
    "/upload-images",
    response_model=List[UploadedFileSchema],
    status_code=status.HTTP_201_CREATED,
    description="Uploads image files to the server",
)
async def upload_images(
    db: Session = Depends(create_session),
    files: List[UploadFile] = File(...),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
) -> List[UploadedFileSchema]:
    """
    Uploads multiple image files for diagnosis.

    Args:
        db (Session): Database session.
        files (List[UploadFile]): The list of image files to upload.
        current_user (UserOutputSchema): The current user performing the upload.

    Returns:
        List[UploadedFileSchema]: A list of schemas representing the uploaded files.
    """
    return FileServices.upload_images(db, files, current_user.id)


# @router.post(
#     "/diagnose-on-upload",
#     response_model=DiagnosisOutputSchema,
#     status_code=status.HTTP_201_CREATED,
#     description="Diagnose an image file uploaded by the current user and save the result to the database.",
# )
# async def diagnose_on_upload(
#     db: Session = Depends(create_session),
#     file: UploadFile = File(...),
#     current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
# ) -> DiagnosisOutputSchema:
#     """
#     Diagnose an image file uploaded by the current user and save the result to the database.

#     Args:
#         db (Session): The database session.
#         file (UploadFile): The image file to diagnose.
#         current_user (UserOutputSchema): The current user uploading the file.

#     Returns:
#         DiagnosisOutputSchema: The schema representing the diagnosis result.
#     """
#     diagnosis_result = DiagnosisServices.diagnose_on_upload(db, file, current_user.id)
#     return diagnosis_result


@router.put(
    "/update-manual-diagnosis",
    response_model=DiagnosisOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Update the manual diagnosis for a diagnosis record.",
)
async def update_manual_diagnosis(
    server_id: str,
    manual_diagnosis: DiseaseTypeEnum,
    db: Session = Depends(create_session),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
) -> DiagnosisOutputSchema:
    """
    Update the manual diagnosis for a diagnosis record.

    Args:
        server_id (int): The ID of the diagnosis record to update.
        manual_diagnosis (DiseaseTypeEnum): The manual diagnosis to set.
        db (Session): The database session.
        current_user (UserOutputSchema): The current authenticated user.

    Returns:
        DiagnosisOutputSchema: The updated diagnosis record.
    """

    return DiagnosisServices.update_manual_diagnosis(
        db,
        server_id,
        current_user.id,
        manual_diagnosis,
    )


@router.get(
    "/get-diagnoses",
    response_model=List[DiagnosisOutputSchema],
    status_code=status.HTTP_200_OK,
    description="Get all diagnosis records for the current user.",
)
async def get_diagnoses(
    db: Session = Depends(create_session),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
) -> List[DiagnosisOutputSchema]:
    """
    Get all diagnosis records for the current user.

    Args:
        db (Session): The database session.
        current_user (UserOutputSchema): The current authenticated user.

    Returns:
        List[DiagnosisOutputSchema]: A list of DiagnosisOutputSchema instances representing the diagnosis records.
    """
    return DiagnosisServices.get_diagnoses(db, current_user.id)


@router.post(
    "/upload-mobile-diagnosis",
    response_model=DiagnosisOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Uploads the mobile diagnosis with an image file to the server.",
)
async def upload_mobile_diagnosis(
    mobile_diagnosis_input: MobileDiagnosisInputSchema,
    db: Session = Depends(create_session),
    file: UploadFile = File(...),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
) -> DiagnosisOutputSchema:
    """
    Uploads an image file to the server.

    Args:
        db (Session): The database session.
        file (UploadFile): The image file to upload.
        current_user (UserOutputSchema): The current user performing the upload.

    Returns:
        UploadedFileSchema: The schema representing the uploaded file.
    """
    return DiagnosisServices.upload_mobile_diagnosis(
        db, file, mobile_diagnosis_input, current_user.id
    )


@router.put(
    "/update-mobile-diagnosis",
    response_model=DiagnosisOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Updates the mobile diagnosis.",
)
async def update_mobile_diagnosis(
    mobile_diagnosis_input: MobileDiagnosisInputSchema,
    db: Session = Depends(create_session),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
) -> DiagnosisOutputSchema:
    """
    Uploads an image file to the server.

    Args:
        db (Session): The database session.
        current_user (UserOutputSchema): The current user performing the upload.

    Returns:
        UploadedFileSchema: The schema representing the uploaded file.
    """
    return DiagnosisServices.update_mobile_diagnosis(
        mobile_diagnosis_input, db, current_user.id
    )
