from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.enums import DiseaseTypeEnum


class DiagnosisOutputSchema(BaseModel):
    id: int
    diagnosis_id: str
    user_idx: int
    server_diagnosis: Optional[DiseaseTypeEnum]
    manual_diagnosis: Optional[DiseaseTypeEnum]
    remark: Optional[str]
    image_path: str
    image_name: str
    is_diagnosed: bool
    created_at: datetime
    confidence_score: Optional[List[float]]

    class Config:
        from_attributes = True


class UploadedFileSchema(BaseModel):
    diagnosis_id: str
    filename: str
    content_type: str
