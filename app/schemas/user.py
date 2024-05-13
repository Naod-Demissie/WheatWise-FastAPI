from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.models.enums import RegionTypeEnum, SexTypeEnum, UserTypeEnum, AccountStatus


# ! update the maximum and the minimum length


class CreateUserSchema(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    prefix: str = Field(..., min_length=2, max_length=10)
    firstname: str = Field(..., min_length=2, max_length=50)
    lastname: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(..., min_length=6, max_length=100)
    # password: str = Field(..., min_length=6, max_length=50)
    sex: SexTypeEnum = Field(...)
    role: UserTypeEnum = UserTypeEnum.USER
    region: RegionTypeEnum = Field(...)
    zone: str = Field(..., min_length=2, max_length=50)
    woreda: str = Field(..., min_length=2, max_length=50)
    organization: str = Field(..., min_length=2, max_length=100)


class UpdateUserDetailSchema(CreateUserSchema):
    profile_pic_base64: Optional[str]

    class Config:
        from_attributes = True



class UserOutputSchema(BaseModel):
    id: int
    user_id: str
    username: str
    prefix: str
    firstname: str
    lastname: str
    email: EmailStr
    sex: SexTypeEnum
    role: UserTypeEnum
    region: RegionTypeEnum
    woreda: str
    zone: str
    organization: str
    password_reset_requested: bool
    first_time_login: bool
    account_status: AccountStatus
    created_at: datetime
    profile_pic_base64: Optional[str] = None

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)


class UpdatePasswordSchema(BaseModel):
    email: EmailStr = Field(..., min_length=6, max_length=100)
    current_password: str = Field(..., min_length=6, max_length=50)
    new_password: str = Field(..., min_length=6, max_length=50)
    new_password2: str = Field(..., min_length=6, max_length=50)


class ModifyUserStatusSchema(BaseModel):
    id: str
    # user_id: str
    note: str


class UpdateUserAccess(BaseModel):
    user_id: str
    note: str
