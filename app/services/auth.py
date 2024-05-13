import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext

from app.utils.session import create_session
from app.models.user import UserModel
from app.schemas.auth import TokenDataSchema, TokenSchema
from app.schemas.user import LoginSchema, UserOutputSchema

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_ALGORITHM = os.getenv("TOKEN_ALGORITHM")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES"))
AUTH_URL = os.getenv("AUTH_URL")
TOKEN_TYPE = os.getenv("TOKEN_TYPE")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class AuthServices:
    """Authentication service."""

    @staticmethod
    def _encrypt_password(plain_password: str) -> str:
        """Encrypt a plain password.

        Args:
            plain_password (str): The plain password to encrypt.

        Returns:
            str: The hashed password.
        """
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(plain_password)

    @staticmethod
    def _verify_password(hashed_password: str, plain_password: str) -> bool:
        """Verify a password against a hash.

        Args:
            hashed_password (str): The hashed password to verify against.
            plain_password (str): The plain password to verify.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _expiration_time() -> str:
        """Get token expiration time.

        Returns:
            str: The token expiration time in "%Y-%m-%d %H:%M:%S" format.
        """
        expires_at = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        return expires_at.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _is_expired(expires_at: str) -> bool:
        """Check if a token has expired.

        Args:
            expires_at (str): The expiration time of the token in "%Y-%m-%d %H:%M:%S" format.

        Returns:
            bool: True if the token has expired, False otherwise.
        """
        return datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") < datetime.utcnow()

    @staticmethod
    def _get_user(db: Session, username: str) -> UserModel:
        """Get a user by username or email.


        Args:
            db (Session): Database session
            username (str): Username or email


        Returns:
            UserModel: User object found
        """
        try:
            user = db.query(UserModel).filter(UserModel.email == username).first()
            if user is None:
                user = (
                    db.query(UserModel).filter(UserModel.username == username).first()
                )
            return user
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    @staticmethod
    def _create_access_token(payload_data: LoginSchema) -> str:
        """Encode user information and expiration time into a JWT access token.

        Args:
            payload_data (LoginSchema): The user login information.

        Returns:
            str: The encoded JWT access token.
        """
        payload = payload_data.model_dump()
        payload["hashed_password"] = AuthServices._encrypt_password(payload["password"])
        payload["expires_at"] = AuthServices._expiration_time()
        payload.pop("password")
        token = jwt.encode(payload, SECRET_KEY, algorithm=TOKEN_ALGORITHM)
        return token

    @staticmethod
    def _verify_access_token(token: str) -> TokenDataSchema:
        """Verify the JWT access token.

        Args:
            token (str): The JWT access token to verify.

        Returns:
            TokenDataSchema: The decoded token data.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM])

            username = payload.get("username")
            hashed_password = payload.get("hashed_password")
            expires_at = payload.get("expires_at")

            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            # if AuthServices._is_expired(expires_at):
            #     raise HTTPException(
            #         status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            #     )

            token_data = TokenDataSchema(
                username=username,
                hashed_password=hashed_password,
                expires_at=expires_at,
            )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        return token_data

    @staticmethod
    def get_current_user(
        token: str = Depends(oauth2_scheme), db: Session = Depends(create_session)
    ) -> UserOutputSchema:
        """Get the current user based on the provided token.

        Args:
            token (str): The token to verify
            db (Session): Database session

        Returns:
            UserOutputSchema: Decoded user schema if user is found
        """
        try:
            if token is None:
                HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            token_data = AuthServices._verify_access_token(token)
            user = AuthServices._get_user(db, username=token_data.username)

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            return UserOutputSchema.model_validate(user)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

    @staticmethod
    def authenticate_user(
        db: Session = Depends(create_session),
        login: OAuth2PasswordRequestForm = Depends(),
    ) -> TokenSchema:
        """Generate a token for the authenticated user.

        Args:
            db (Session, optional): Database session. Defaults to Depends(create_session).
            login (OAuth2PasswordRequestForm, optional): Form containing the username
                or email and password.


        Returns:
            TokenSchema: An instance of TokenSchema containing the access token and token type.
        """
        try:
            user = AuthServices._get_user(db, login.username)

            if user is None or user.password is None:

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                )

            if not AuthServices._verify_password(user.password, login.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                )

            access_token = AuthServices._create_access_token(
                LoginSchema(username=login.username, password=login.password)
            )
            return TokenSchema(access_token=access_token, token_type=TOKEN_TYPE)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
