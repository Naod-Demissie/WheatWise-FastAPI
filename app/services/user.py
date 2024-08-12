import base64
from datetime import datetime, timedelta
import os
import random
from uuid import uuid4
from dotenv import load_dotenv
from fastapi import HTTPException, status
from typing import List, Optional
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.models.enums import *

from app.models.user import PasswordReset, UserModel
from app.schemas.user import (
    CreateUserSchema,
    UpdatePasswordSchema,
    UpdateUserDetailSchema,
    UserOutputSchema,
)
from app.utils.session import SessionFactory

load_dotenv()
OTP_SENDER_EMAIL = os.getenv("OTP_SENDER_EMAIL")
OTP_EXPIRE_TIME = int(os.getenv("OTP_EXPIRE_TIME"))


class UserServices:
    @staticmethod
    def create_user(
        db: Session,
        user_data: CreateUserSchema,
        current_user: UserOutputSchema,
    ) -> UserOutputSchema:
        """
        Create a new user.

        Args:
            db (Session): Database session
            user_data (CreateUserSchema): User data
            current_user (UserOutputSchema): Current user data

        Returns:
            UserOutputSchema: Created user data
        """
        try:
            if current_user.role == "User":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admin users can create a new user.",
                )
            if current_user.role == "Admin" and user_data.role != "User":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin can only create users with a user role",
                )

            new_user = UserModel(**user_data.model_dump())
            new_user.user_id = uuid4().hex
            new_user.profile_pic_path = os.getenv("PROFILE_PATH")
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            user = (
                db.query(UserModel).filter(UserModel.email == user_data.email).first()
            )

            UserServices.request_password_reset(db, user.email)

            password_log = (
                db.query(PasswordReset)
                .filter(PasswordReset.user_idx == user.id)
                .first()
            )
            user.password = password_log.secret_key
            user.set_password(user.password)
            db.add(user)
            db.commit()
            db.refresh(user)

            return UserOutputSchema.model_validate(user)

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create a new user.",
            )

    @staticmethod
    def create_default_user(db: Session = SessionFactory()):
        """
        Create a default admin user if no users exist in the database.

        Args:
            db (Session): Database session (default: SessionFactory())

        Returns:
            None
        """
        users = db.query(UserModel).all()
        if len(users) == 0:
            new_admin = UserModel(
                username=os.getenv("SYS_ADMIN_USERNAME"),
                prefix=os.getenv("SYS_ADMIN_PREFIX"),
                firstname=os.getenv("SYS_ADMIN_FIRSTNAME"),
                lastname=os.getenv("SYS_ADMIN_LASTNAME"),
                email=os.getenv("SYS_ADMIN_EMAIL"),
                password=os.getenv("SYS_ADMIN_PASSWORD"),
                role=UserTypeEnum[os.getenv("SYS_ADMIN_ROLE")],
                region=RegionTypeEnum[os.getenv("SYS_ADMIN_REGION")],
                zone=os.getenv("SYS_ADMIN_ZONE"),
                woreda=os.getenv("SYS_ADMIN_WOREDA"),
                sex=os.getenv("SYS_ADMIN_SEX"),
                organization=os.getenv("SYS_ADMIN_ORGANIZATION"),
                first_time_login=False,
                user_id=uuid4().hex,
                profile_pic_path=os.getenv("PROFILE_PATH"),
            )
            new_admin.set_password(new_admin.password)
            db.add(new_admin)
            db.commit()
            db.close()

    @staticmethod
    def get_user(db: Session, user_id: str) -> UserOutputSchema:
        """
        Get a user by user ID.

        Args:
            db (Session): Database session
            user_id (str): UUID of the current user

        Returns:
            UserOutputSchema: Current user's data

        """
        try:
            user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            if user.profile_pic_path is not None:
                with open(user.profile_pic_path, "rb") as img_file:
                    img_data = img_file.read()
                    base64_encoded = base64.b64encode(img_data)
                    base64_string = base64_encoded.decode("utf-8")

            profile_pic_base64 = base64_string if user.profile_pic_path else None

            return UserOutputSchema(
                id=user.id,
                user_id=user.user_id,
                username=user.username,
                prefix=user.prefix,
                firstname=user.firstname,
                lastname=user.lastname,
                email=user.email,
                sex=user.sex,
                role=user.role,
                region=user.region,
                woreda=user.woreda,
                zone=user.zone,
                organization=user.organization,
                password_reset_requested=user.password_reset_requested,
                first_time_login=user.first_time_login,
                account_status=user.account_status,
                created_at=user.created_at,
                profile_pic_base64=profile_pic_base64,
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User not found",
            )

    @staticmethod
    def get_users(
        db: Session,
        current_user: UserOutputSchema,
        organization: Optional[str] = None,
    ) -> List[UserOutputSchema]:
        """
        Get a list of users with optional selection criteria.

        Args:
            db (Session): Database session
            current_user (UserOutputSchema): Current user data
            organization (Optional[str]): organization to filter by

        Returns:
            List[UserOutputSchema]: List of users data

        """
        try:
            if current_user.role == "User":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admin users can access this endpoint.",
                )
            users = db.query(UserModel)
            if organization:
                users = users.filter(UserModel.organization == organization)
            users = users.all()
            return [UserOutputSchema.model_validate(user) for user in users]

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users data",
            )

    def get_user_fullname(db: Session, user_id: str) -> dict:
        """
        Get the full name of the current user.

        Args:
            db (Session): Database session
            user_id (str): UUID of the current user

        Returns:
            dict: Dictionary containing the full name of the current user
        """

        try:
            user = UserServices.get_user(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            return {"fullname": f"{user.firstname} {user.lastname}"}

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user fullname",
            )

    @staticmethod
    def update_profile(
        db: Session, user_id: str, update_data: UpdateUserDetailSchema
    ) -> UserOutputSchema:
        """
        Update the profile data for a user.

        Args:
            db (Session): Database session
            user_id (str): UUID of the current user
            update_data (UpdateUserDetailSchema): Updated profile data

        Returns:
            UserOutputSchema: Updated user profile data
        """
        try:
            user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            user.username = update_data.username
            user.prefix = update_data.prefix
            user.firstname = update_data.firstname
            user.lastname = update_data.lastname
            user.email = update_data.email
            user.role = update_data.role
            user.sex = update_data.sex
            user.region = update_data.region
            user.zone = update_data.zone
            user.woreda = update_data.woreda
            user.organization = update_data.organization

            if update_data.profile_pic_base64 is not None:
                base64_string = update_data.profile_pic_base64
                decoded_image = base64.b64decode(base64_string)

                profile_folder_path = (
                    os.getenv("PROFILE_FOLDER_PATH")
                    + "/"
                    # + "".join(random.choices("0123456789", k=6))
                    + user_id
                    + ".png"
                )

                with open(profile_folder_path, "wb") as f:
                    f.write(decoded_image)

                user.profile_pic_path = profile_folder_path

            db.commit()
            return UserOutputSchema.model_validate(user)

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to update user profile",
            )

    @staticmethod
    def update_password(db: Session, password_data: UpdatePasswordSchema) -> dict:
        """
        Update the password for a user.

        Args:
            db (Session): Database session
            password_data (UpdatePasswordSchema): Update password data including current password, new password, and confirm new password

        Returns:
            dict: Dictionary containing a message confirming the password update
        """

        try:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            user = (
                db.query(UserModel)
                .filter(UserModel.email == password_data.email)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            if user.password_reset_requested:
                password_log = (
                    db.query(PasswordReset)
                    .filter(PasswordReset.user_idx == user.id)
                    .first()
                )

                if password_data.current_password != password_log.secret_key:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="OTP is incorrect. Enter the correct OTP.",
                    )

                if (
                    password_log.timestamp + timedelta(hours=OTP_EXPIRE_TIME)
                    < datetime.now()
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="OTP has expired.",
                    )

                # Update the password
                user.password = pwd_context.hash(password_data.new_password)
                user.password_reset_requested = False

                if user.first_time_login:
                    user.first_time_login = False

                db.delete(password_log)
                db.commit()
                return {"message": "Password updated successfully"}

            else:
                if not pwd_context.verify(
                    password_data.current_password, user.password
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Current password is incorrect.",
                    )

                if password_data.new_password != password_data.new_password2:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="New passwords do not match",
                    )

                # Update the password
                user.password = pwd_context.hash(password_data.new_password)
                user.password_reset_requested = False

                if user.first_time_login:
                    user.first_time_login = False

                db.commit()
                return {"message": "Password updated successfully"}

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),  #! changed this
            )

    @staticmethod
    def request_password_reset(db: Session, email: EmailStr):
        """
        Send OTP to the user's email for password reset.

        Args:
            db (Session): Database session
            password_reset_data (ResetPasswordSchema): Reset password data including email

        Returns:
            dict: Dictionary containing a message confirming the OTP sent
        """
        import random
        from app.utils.mail import send_otp

        try:
            user = db.query(UserModel).filter(UserModel.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            otp = "".join(random.choices("0123456789", k=6))
            send_otp(OTP_SENDER_EMAIL, user.email, otp)

            password_log = PasswordReset(user_idx=user.id, secret_key=otp)
            user.password_reset_requested = True

            db.add(password_log)
            db.commit()
            db.refresh(password_log)
            return {"message": "OTP sent to your email"}

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset OTP",
            )
