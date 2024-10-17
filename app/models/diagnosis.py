from datetime import datetime
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    Enum as PgEnum,
    ForeignKey,
)
from app.models.enums import DiseaseTypeEnum
from app.utils.session import Base, engine
from sqlalchemy.orm import relationship


class DiagnosisModel(Base):
    """Represents a diagnosis entry from a user."""

    __tablename__ = "diagnosis"
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(String, unique=True, nullable=False)
    mobile_id = Column(String, unique=True, nullable=False)
    user_idx = Column(Integer, ForeignKey("users.id"), nullable=False)
    server_diagnosis = Column(PgEnum(DiseaseTypeEnum), nullable=True)
    mobile_diagnosis = Column(PgEnum(DiseaseTypeEnum), nullable=True)
    manual_diagnosis = Column(PgEnum(DiseaseTypeEnum), nullable=True)
    remark = Column(String, nullable=True)
    mobile_image_path = Column(String, nullable=True)
    server_image_path = Column(String, nullable=False)
    image_name = Column(String, nullable=False)
    is_server_diagnosed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    server_confidence_score = Column(JSON, nullable=True)
    mobile_confidence_score = Column(JSON, nullable=True)
    user = relationship("UserModel", back_populates="diagnosis")


Base.metadata.create_all(bind=engine)
