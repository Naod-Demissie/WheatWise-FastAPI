from typing import List, Optional
from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import status, Depends, APIRouter

from app.schemas.user import (
    UserOutputSchema,
    UpdatePasswordSchema,
    CreateUserSchema,
)
from app.services.auth import AuthServices
from app.services.user import UserServices
from app.utils.session import create_session


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/create-user",
    response_model=UserOutputSchema,
    status_code=status.HTTP_201_CREATED,
    description="Create a new user.",
)
def create_user(
    user_data: CreateUserSchema,
    db: Session = Depends(create_session),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
) -> UserOutputSchema:
    """
    Create a new user.

    Args:
    - user_data (CreateUserSchema): User data to create a new user
    - db (Session): Database session
    - current_user (UserOutputSchema): Current user data

    Returns:
    - UserOutputSchema: Created user data
    """
    return UserServices.create_user(db, user_data, current_user)


@router.get(
    "/get-user",
    response_model=UserOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Get the current user.",
)
def get_user(
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
    db: Session = Depends(create_session),
) -> UserOutputSchema:
    """
    Get the current user's data.

    Args:
    - current_user (UserOutputSchema): Current user data
    - db (Session): Database session

    Returns:
    - UserOutputSchema: Current user's data
    """
    return UserServices.get_user(db, current_user.user_id)


@router.get(
    "/get-users",
    response_model=List[UserOutputSchema],
    status_code=status.HTTP_200_OK,
    description="Get a list of users with optional selection criteria.",
)
def get_users(
    organization: Optional[str] = None,
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
    db: Session = Depends(create_session),
) -> List[UserOutputSchema]:
    """
    Get a list of users with optional selection criteria.

    Args:
    - organization (str, optional): organization to filter by
    - current_user (UserOutputSchema): Current user data
    - db (Session): Database session

    Returns:
    - List[UserOutputSchema]: List of users data
    """
    return UserServices.get_users(db, current_user, organization=organization)


@router.get(
    "/fullname",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    description="Get the full name of the current user.",
)
def get_user_fullname(
    db: Session = Depends(create_session),
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
) -> dict:
    """
    Get the full name of the current user.

    Args:
    - current_user (UserOutputSchema): Current user data
    - db (Session): Database session

    Returns:
    - dict: Dictionary containing the full name of the current user
    """
    return UserServices.get_user_fullname(db, current_user.user_id)


@router.put(
    "/update-profile",
    response_model=UserOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Update the profile data for the current user.",
)
def update_profile(
    update_data: CreateUserSchema,
    current_user: UserOutputSchema = Depends(AuthServices.get_current_user),
    db: Session = Depends(create_session),
) -> UserOutputSchema:
    """
    Update the profile data for the current user.

    Args:
    - update_data (CreateUserSchema): Updated profile data
    - current_user (UserOutputSchema): Current user data
    - db (Session): Database session

    Returns:
    - UserOutputSchema: Updated user profile data
    """
    return UserServices.update_profile(db, current_user.user_id, update_data)


@router.put(
    "/update-password",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    description="Update the password for the current user.",
)
def update_password(
    update_data: UpdatePasswordSchema,
    db: Session = Depends(create_session),
) -> dict:
    """
    Update the password for the current user.

    Args:
    - update_data (UpdatePasswordSchema): Update password data including current password, new password, and confirm new password
    - db (Session): Database session

    Returns:
    - dict: Dictionary containing a message confirming the password update
    """
    return UserServices.update_password(db, update_data)


@router.put(
    "/request-password-reset",
    response_model=dict,
    description="Reset the password for the current user using an OTP.",
)
def request_password_reset(
    email: EmailStr,
    db: Session = Depends(create_session),
) -> dict:
    """
    Reset the password for the current user using an OTP.

    Args:
    - reset_data (ResetPasswordSchema): Reset password data including email and OTP
    - current_user (UserOutputSchema): Current user data
    - db (Session): Database session

    Returns:
    - dict: Dictionary containing a message confirming the password reset
    """

    return UserServices.request_password_reset(db, email)
