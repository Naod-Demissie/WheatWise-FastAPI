from datetime import datetime
from uuid import uuid4
from app.utils.session import Base, engine
from app.models.enums import AccountStatus, RegionTypeEnum, SexTypeEnum, UserTypeEnum
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum as PgEnum,
)

from sqlalchemy.orm import relationship
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(Base):
    """Represents a user in the system."""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False, default=uuid4().hex)
    username = Column(String, unique=True, nullable=False, index=True)
    prefix = Column(String, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=True)
    sex = Column(PgEnum(SexTypeEnum), nullable=False)
    region = Column(PgEnum(RegionTypeEnum), nullable=False)
    zone = Column(String, nullable=False)
    woreda = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    role = Column(PgEnum(UserTypeEnum), nullable=False, default=UserTypeEnum.USER)
    first_time_login = Column(Boolean, nullable=False, default=True)
    password_reset_requested = Column(Boolean, nullable=False, default=False)
    account_status = Column(PgEnum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    password_resets = relationship("PasswordReset", back_populates="account", cascade="all, delete-orphan")
    diagnosis = relationship("DiagnosisModel", back_populates="user", cascade="all, delete-orphan")
    profile_pic_path = Column(String, nullable=True)

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    def check_password(self, password: str):
        return pwd_context.verify(password, self.password)


class PasswordReset(Base):
    """Represents a password reset request log for a user."""

    __tablename__ = "password_reset_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_idx = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    secret_key = Column(String, nullable=True)
    account = relationship("UserModel", back_populates="password_resets")


Base.metadata.create_all(bind=engine)


# from datetime import datetime
# from uuid import uuid4
# from app.utils.session import Base, engine
# from app.models.enums import AccountStatus, RegionTypeEnum, SexTypeEnum, UserTypeEnum
# from sqlalchemy import (
#     Column,
#     ForeignKey,
#     Integer,
#     String,
#     Boolean,
#     DateTime,
#     Enum as PgEnum,
# )

# from sqlalchemy.orm import relationship
# from passlib.context import CryptContext


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# class UserModel(Base):
#     """Represents a user in the system."""
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(String, unique=True, nullable=False, default=uuid4().hex)
#     username = Column(String, unique=True, nullable=False, index=True)
#     prefix = Column(String, nullable=False)
#     firstname = Column(String, nullable=False)
#     lastname = Column(String, nullable=False)
#     email = Column(String, unique=True, nullable=False, index=True)
#     password = Column(String, nullable=True)
#     sex = Column(PgEnum(SexTypeEnum), nullable=False)
#     region = Column(PgEnum(RegionTypeEnum), nullable=False)
#     zone = Column(String, nullable=False)
#     woreda = Column(String, nullable=False)
#     organization = Column(String, nullable=False)
#     role = Column(PgEnum(UserTypeEnum), nullable=False, default=UserTypeEnum.USER)
#     first_time_login = Column(Boolean, nullable=False, default=True)
#     password_reset_requested = Column(Boolean, nullable=False, default=False)
#     account_status = Column(PgEnum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)
#     created_at = Column(DateTime, nullable=False, default=datetime.now)
#     deleted_at = Column(DateTime, nullable=True)
#     password_resets = relationship("PasswordReset", back_populates="account", cascade="all, delete-orphan")
#     diagnosis = relationship("DiagnosisModel", back_populates="user", cascade="all, delete-orphan")

#     def set_password(self, password: str):
#         self.password = pwd_context.hash(password)

#     def check_password(self, password: str):
#         return pwd_context.verify(password, self.password)


# class PasswordReset(Base):
#     """Represents a password reset request log for a user."""
#     __tablename__ = "password_reset_log"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_idx = Column(Integer, ForeignKey("users.id"), nullable=False)
#     timestamp = Column(DateTime, default=datetime.now, nullable=False)
#     secret_key = Column(String, nullable=True)
#     account = relationship("UserModel", back_populates="password_resets")


# Base.metadata.create_all(bind=engine)
