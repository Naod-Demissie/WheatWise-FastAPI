from typing import List, Optional
from fastapi import File, UploadFile
from pydantic import BaseModel, model_validator
from datetime import datetime
from app.models.enums import DiseaseTypeEnum
import json


class DiagnosisOutputSchema(BaseModel):
    id: int
    server_id: str
    mobile_id: str
    user_idx: int
    server_diagnosis: Optional[DiseaseTypeEnum]
    mobile_diagnosis: Optional[DiseaseTypeEnum]
    manual_diagnosis: Optional[DiseaseTypeEnum]
    mobile_image_path: str
    server_image_path: str
    remark: Optional[str]
    image_name: str
    is_server_diagnosed: bool
    created_at: datetime
    server_confidence_score: Optional[List[float]]
    mobile_confidence_score: Optional[List[float]]

    class Config:
        from_attributes = True


class MobileDiagnosisInputSchema(BaseModel):
    mobile_id: str
    mobile_diagnosis: Optional[DiseaseTypeEnum]
    manual_diagnosis: Optional[DiseaseTypeEnum]
    mobile_image_path: str
    remark: Optional[str]
    file_name: str
    mobile_confidence_score: Optional[List[float]]

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    class Config:
        from_attributes = True


class UploadedFileSchema(BaseModel):
    server_id: str
    filename: str
    content_type: str
