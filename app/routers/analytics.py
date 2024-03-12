from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from app.schemas.user import UserOutputSchema
from app.services.auth import AuthServices

from app.utils.session import create_session, engine
from app.services.analytics import AnalyticsServices


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/get-diagnosis-report",
    status_code=status.HTTP_200_OK,
    description="Get the confusion matrix image for the diagnosis report.",
)
async def get_diagnosis_report(
    db: Session = Depends(create_session),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
    return_json: bool = True,
):
    """
    Get the confusion matrix image for the diagnosis report.

    Args:
        - db (Session): The database session. Defaults to Depends(create_session).
        - current_user (UserOutputSchema): The current user data
        - return_json (bool): If True, return the diagnosis report as a JSON object.
                              If False, return the confusion matrix image as a PNG image stream.

    Returns:
        - StreamingResponse: If return_json is False, returns the confusion matrix image stream.
                             Otherwise, returns a JSON object with the diagnosis report.
    """
    if return_json:
        return await AnalyticsServices.get_diagnosis_report(
            db, current_user, return_json
        )

    image_stream = await AnalyticsServices.get_diagnosis_report(
        db, current_user, return_json
    )
    return StreamingResponse(image_stream, media_type="image/png")


@router.get(
    "/get-system-report",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    description="Get a report of the system including sizes of the database table and upload files.",
)
async def get_system_report(
    db: Session = Depends(create_session),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
) -> dict:
    """
    Get a report of the system including sizes of the database table and upload files.

    Args:
        - db (Session): The database session.
        - current_user (UserOutputSchema): The current user data

    Returns:
        - dict: A schema containing the database report and upload report.
    """
    return await AnalyticsServices.get_system_report(db, current_user)
