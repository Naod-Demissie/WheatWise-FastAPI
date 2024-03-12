from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.utils import session

from app.schemas.auth import TokenSchema
from app.services.auth import AuthServices


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenSchema,
    description="Authenticate user and generate access token.",
)
async def login(
    db: session = Depends(session.create_session),
    login: OAuth2PasswordRequestForm = Depends(),
) -> TokenSchema:
    """Authenticate the user and generate a token.

    Args:
        db (Session, optional): The database session
        login (OAuth2PasswordRequestForm, optional): The login form containing the username
            and password

    Returns:
        TokenSchema: An instance of TokenSchema containing the access token and token type.
    """
    return AuthServices.authenticate_user(db, login)
