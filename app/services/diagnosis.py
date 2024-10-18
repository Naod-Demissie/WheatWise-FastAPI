import os
import imghdr
import shutil
from PIL import Image
from typing import List
from uuid import uuid4
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.params import Depends
from app.models.enums import DiseaseTypeEnum
from app.schemas.diagnosis import (
    DiagnosisOutputSchema,
    MobileDiagnosisInputSchema,
    UploadedFileSchema,
)
from app.models.diagnosis import DiagnosisModel
from sqlalchemy.orm import Session

import numpy as np

import torch
import torchvision.transforms as transforms

from app.utils.session import SessionFactory
import base64


load_dotenv()
UPLOAD_FOLDER_PATH = os.getenv("UPLOAD_FOLDER_PATH")

router = APIRouter(prefix="/diagnosis", tags=["Diagnosis"])


class FileServices:
    """
    Provides methods for uploading and managing image files.
    """

    #! change the file names when saving
    @staticmethod
    def upload_image(
        db: Session, file: UploadFile, user_idx: int
    ) -> UploadedFileSchema:
        """
        Uploads an image file, saves it to the specified folder, and creates a record in the database.

        Args:
            db (Session): Database session.
            file (UploadFile): The image file to upload.
            user_idx (int): The id of the current user.


        Returns:
            UploadedFileSchema: The schema representing the uploaded file.
        """
        try:
            # Check if the uploaded file is an image
            if file.content_type not in [
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/bmp",
            ]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only image files (JPEG, PNG, GIF, BMP) are allowed.",
                )

            # You can also add an additional check using the imghdr module
            file_extension = imghdr.what(file.file)
            if file_extension not in ["jpeg", "png", "gif", "bmp"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File is not a valid image type.",
                )

            server_image_path = f"{UPLOAD_FOLDER_PATH}/{file.filename}"
            with open(server_image_path, "wb") as image_file:
                shutil.copyfileobj(file.file, image_file)

            uploaded_file = DiagnosisModel(
                user_idx=user_idx,
                server_id=uuid4().hex,
                server_image_path=server_image_path,
                image_name=file.filename,
            )

            db.add(uploaded_file)
            db.commit()
            db.refresh(uploaded_file)

            return UploadedFileSchema(
                server_id=uploaded_file.server_id,
                filename=file.filename,
                content_type=file.content_type,
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file",
            )

    @staticmethod
    def upload_images(
        db: Session, files: List[UploadFile], user_idx: int
    ) -> List[UploadedFileSchema]:
        """
        Uploads a list of image files, saves them to the specified folder, and creates records in the database.

        Args:
            db (Session): The database session.
            files (List[UploadFile]): The list of image files to upload.
            user_id (int): The ID of the current user.

        Returns:
            List[UploadedFileSchema]: A list of schemas representing the uploaded files.
        """
        try:
            uploaded_files = []
            for file in files:
                # Check if the uploaded file is an image
                if file.content_type not in [
                    "image/jpeg",
                    "image/png",
                    "image/gif",
                    "image/bmp",
                ]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Only image files (JPEG, PNG, GIF, BMP) are allowed.",
                    )

                # You can also add an additional check using the imghdr module
                file_extension = imghdr.what(file.file)
                if file_extension not in ["jpeg", "png", "gif", "bmp"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File is not a valid image type.",
                    )
                server_image_path = f"{UPLOAD_FOLDER_PATH}/{file.filename}"
                with open(server_image_path, "wb") as image_file:
                    shutil.copyfileobj(file.file, image_file)

                uploaded_file = DiagnosisModel(
                    server_id=uuid4().hex,
                    user_idx=user_idx,
                    server_image_path=server_image_path,
                    image_name=file.filename,
                )
                db.add(uploaded_file)
                db.commit()
                db.refresh(uploaded_file)
                uploaded_files.append(
                    UploadedFileSchema(
                        server_id=uploaded_file.server_id,
                        filename=file.filename,
                        content_type=file.content_type,
                    )
                )
            return uploaded_files
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload files",
            )


# class FileServices:
#     """
#     Provides methods for uploading and managing image files.
#     """

#     #! change the file names when saving
#     @staticmethod
#     def upload_image(
#         db: Session, file: UploadFile, user_idx: int
#     ) -> UploadedFileSchema:
#         """
#         Uploads an image file, saves it to the specified folder, and creates a record in the database.

#         Args:
#             db (Session): Database session.
#             file (UploadFile): The image file to upload.
#             user_idx (int): The id of the current user.


#         Returns:
#             UploadedFileSchema: The schema representing the uploaded file.
#         """
#         try:
#             server_image_path = f"{UPLOAD_FOLDER_PATH}/{file.filename}"
#             with open(server_image_path, "wb") as image_file:
#                 shutil.copyfileobj(file.file, image_file)

#             uploaded_file = DiagnosisModel(
#                 user_idx=user_idx,
#                 server_id=uuid4().hex,
#                 server_image_path=server_image_path,
#                 image_name=file.filename,
#             )

#             db.add(uploaded_file)
#             db.commit()
#             db.refresh(uploaded_file)

#             return UploadedFileSchema(
#                 server_id=uploaded_file.server_id,
#                 filename=file.filename,
#                 content_type=file.content_type,
#             )

#         except Exception as e:
#             print(e)
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to upload file",
#             )

#     @staticmethod
#     def upload_images(
#         db: Session, files: List[UploadFile], user_idx: int
#     ) -> List[UploadedFileSchema]:
#         """
#         Uploads a list of image files, saves them to the specified folder, and creates records in the database.

#         Args:
#             db (Session): The database session.
#             files (List[UploadFile]): The list of image files to upload.
#             user_id (int): The ID of the current user.

#         Returns:
#             List[UploadedFileSchema]: A list of schemas representing the uploaded files.
#         """
#         try:
#             uploaded_files = []
#             for file in files:
#                 server_image_path = f"{UPLOAD_FOLDER_PATH}/{file.filename}"
#                 with open(server_image_path, "wb") as image_file:
#                     shutil.copyfileobj(file.file, image_file)

#                 uploaded_file = DiagnosisModel(
#                     server_id=uuid4().hex,
#                     user_idx=user_idx,
#                     server_image_path=server_image_path,
#                     image_name=file.filename,
#                 )
#                 db.add(uploaded_file)
#                 db.commit()
#                 db.refresh(uploaded_file)
#                 uploaded_files.append(
#                     UploadedFileSchema(
#                         server_id=uploaded_file.server_id,
#                         filename=file.filename,
#                         content_type=file.content_type,
#                     )
#                 )
#             return uploaded_files
#         except Exception as e:
#             print(e)
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to upload files",
#             )


class DiagnosisServices:
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    batch_size = 12

    @staticmethod
    def load_model(model_path: str) -> torch.nn.Module:
        """
        Load a PyTorch model from the specified path.

        Args:
            model_path (str): The path to the PyTorch model file.

        Returns:
            torch.nn.Module: The loaded PyTorch model.
        """
        # model = torch.load(model_path) #! delete if not needed
        model = torch.jit.load(model_path)
        model.to(DiagnosisServices.device)
        model.eval()
        return model

    @staticmethod
    def _diagnose_image(image_path: str) -> list:
        """
        Diagnose an image using the loaded PyTorch model.

        Args:
            image_path (str): The path to the image file.

        Returns:
            list: A list of probabilities for each class.
        """
        from app.main import model

        image = Image.open(image_path)
        image = image.convert("RGB")

        image = (
            DiagnosisServices.transform(image).unsqueeze(0).to(DiagnosisServices.device)
        )

        with torch.no_grad():
            output = model(image)

        probs = torch.nn.functional.softmax(output[0], dim=0)

        probs = probs.data.cpu().numpy().tolist()
        return probs

    @staticmethod
    def _decode_prediction(probs: List[float]) -> DiseaseTypeEnum:
        """
        Decode the prediction probabilities into a disease type.

        Args:
            probs (List[float]): A list of probabilities for each disease type.

        Returns:
            DiseaseTypeEnum: The predicted disease type.
        """
        disease_types = {  #! change the order to match them model output
            0: DiseaseTypeEnum.BROWN_RUST,
            1: DiseaseTypeEnum.YELLOW_RUST,
            2: DiseaseTypeEnum.SEPTORIA,
            3: DiseaseTypeEnum.HEALTHY,
            4: DiseaseTypeEnum.MILDEW,
        }
        max_index = np.argmax(probs)
        return disease_types[max_index]

    @staticmethod
    def diagnose_on_upload(
        db: Session, file: UploadFile, user_idx: int
    ) -> DiagnosisOutputSchema:
        """
        Diagnose an image file uploaded by a user and save the result to the database.

        Args:
            db (Session): The database session.
            file (UploadFile): The image file to diagnose.
            user_idx (int): The ID of the current user.

        Returns:
            DiagnosisOutputSchema: The schema representing the diagnosis result.
        """
        try:
            server_image_path = f"{UPLOAD_FOLDER_PATH}/{file.filename}"
            with open(server_image_path, "wb") as image_file:
                shutil.copyfileobj(file.file, image_file)

            probs = DiagnosisServices._diagnose_image(server_image_path)
            server_diagnosis = DiagnosisServices._decode_prediction(probs)

            uploaded_file = DiagnosisModel(
                user_idx=user_idx,
                server_image_path=server_image_path,
                server_id=uuid4().hex,
                image_name=file.filename,
                server_diagnosis=server_diagnosis,
                is_server_diagnosed=True,
                server_confidence_score=probs,
            )

            db.add(uploaded_file)
            db.commit()
            db.refresh(uploaded_file)
            return DiagnosisOutputSchema.model_validate(uploaded_file)

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to diagnose image",
            )

    @staticmethod
    def update_manual_diagnosis(
        db: Session,
        server_id: str,
        user_idx: int,
        manual_diagnosis: DiseaseTypeEnum,
    ) -> DiagnosisOutputSchema:
        """
        Update the manual diagnosis for a diagnosis record and return the updated record as DiagnosisOutputSchema.

        Args:
            db (Session): The database session.
            server_id (str): The UUID of the diagnosis record to update.
            user_idx (int): The ID of the current user.
            manual_diagnosis (DiseaseTypeEnum): The manual diagnosis to set.

        Returns:
            DiagnosisOutputSchema: The updated diagnosis record.
        """
        try:
            diagnosis = (
                db.query(DiagnosisModel)
                .filter(DiagnosisModel.user_idx == user_idx)
                .filter(DiagnosisModel.server_id == server_id)
                .first()
            )
            if not diagnosis:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Diagnosis record not found",
                )

            diagnosis.manual_diagnosis = manual_diagnosis
            db.commit()
            return DiagnosisOutputSchema.model_validate(diagnosis)

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update manual diagnosis",
            )

    @staticmethod
    #! this only get the diagnosis by the current user. change this to return all diagnosis for admin user
    def get_diagnoses(db: Session, user_idx: int) -> List[DiagnosisOutputSchema]:
        """
        Get all diagnosis records for the current user from the database.

        Args:
            db (Session): The SQLAlchemy database session.
            user_idx (int): The ID of the current user.

        Returns:
            List[DiagnosisOutputSchema]: A list of DiagnosisOutputSchema instances representing the diagnosis records.
        """

        try:
            diagnoses = (
                db.query(DiagnosisModel)
                .filter(DiagnosisModel.user_idx == user_idx)
                .all()
            )
            return [
                DiagnosisOutputSchema.model_validate(diagnosis)
                for diagnosis in diagnoses
            ]

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve diagnosis records",
            )

    @staticmethod
    def batch_diagnose_uploaded_images(
        db: Session = SessionFactory(),
    ) -> List[DiagnosisOutputSchema]:
        """
        Diagnose images for all uploaded files that are not yet diagnosed.

        Args:
            db (Session): The database session.

        Returns:
            List[DiagnosisOutputSchema]: A list of DiagnosisOutputSchema instances representing the diagnosis results.
        """

        try:
            from torch.utils.data import DataLoader
            from app.main import model
            from app.utils.dataset import CustomDataset

            uploaded_files = (
                db.query(DiagnosisModel)
                .filter(DiagnosisModel.is_server_diagnosed == False)
                .all()
            )

            image_paths = [
                uploaded_file.server_image_path for uploaded_file in uploaded_files
            ]

            dataset = CustomDataset(image_paths, transform=DiagnosisServices.transform)
            dataloader = DataLoader(
                dataset, batch_size=DiagnosisServices.batch_size, shuffle=False
            )

            probs = []
            for batch_images in dataloader:
                batch_images = batch_images.to(DiagnosisServices.device)
                with torch.no_grad():
                    output = model(batch_images)
                prob = torch.nn.functional.softmax(output, dim=0)
                prob = prob.data.cpu().numpy().tolist()
                probs.extend(prob)

            results = []
            for i, uploaded_file in enumerate(uploaded_files):
                uploaded_file.server_diagnosis = DiagnosisServices._decode_prediction(
                    probs[i]
                )

                uploaded_file.is_server_diagnosed = True
                uploaded_file.server_confidence_score = probs[i]

                diagnosis_output = DiagnosisOutputSchema.model_validate(uploaded_file)
                results.append(diagnosis_output)

            db.commit()
            return results
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to diagnose uploaded files",
            )

    def upload_mobile_diagnosis(
        db: Session,
        file: UploadFile,
        mobile_diagnosis_input: MobileDiagnosisInputSchema,
        user_idx: int,
    ) -> DiagnosisOutputSchema:
        """
        Uploads an image file, saves it to the specified folder, and creates a record in the database.

        Args:
            db (Session): Database session.
            file (UploadFile): The image file to upload.
            user_idx (int): The id of the current user.

        Returns:
            DiagnosisOutputSchema: The schema representing the uploaded file.
        """
        try:
            server_image_path = f"{UPLOAD_FOLDER_PATH}/{file.filename}"
            with open(server_image_path, "wb") as image_file:
                shutil.copyfileobj(file.file, image_file)

            uploaded_diagnosis = DiagnosisModel(
                user_idx=user_idx,
                server_id=uuid4().hex,
                mobile_id=mobile_diagnosis_input.mobile_id,
                server_image_path=server_image_path,
                image_name=file.filename,
                mobile_diagnosis=mobile_diagnosis_input.mobile_diagnosis,
                # manual_diagnosis=mobile_diagnosis_input.manual_diagnosis,
                remark=mobile_diagnosis_input.remark,
                mobile_image_path=mobile_diagnosis_input.mobile_image_path,
                mobile_confidence_score=mobile_diagnosis_input.mobile_confidence_score,
            )

            print(mobile_diagnosis_input.manual_diagnosis)

            db.add(uploaded_diagnosis)
            db.commit()
            db.refresh(uploaded_diagnosis)

            return DiagnosisOutputSchema.model_validate(uploaded_diagnosis)

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
                # detail="Failed to upload file",
            )

    def update_mobile_diagnosis(
        mobile_diagnosis_input: MobileDiagnosisInputSchema,
        db: Session,
        user_idx: int,
    ) -> DiagnosisOutputSchema:
        """
        Uploads an image file, saves it to the specified folder, and creates a record in the database.

        Args:
            db (Session): Database session.
            file (UploadFile): The image file to upload.
            user_idx (int): The id of the current user.

        Returns:
            DiagnosisOutputSchema: The schema representing the uploaded file.
        """
        try:
            uploaded_diagnosis = (
                db.query(DiagnosisModel)
                .filter(DiagnosisModel.mobile_id == mobile_diagnosis_input.mobile_id)
                .first()
            )
            uploaded_diagnosis.mobile_diagnosis = (
                mobile_diagnosis_input.mobile_diagnosis
            )
            uploaded_diagnosis.manual_diagnosis = (
                mobile_diagnosis_input.manual_diagnosis
            )
            uploaded_diagnosis.remark = mobile_diagnosis_input.remark

            uploaded_diagnosis.mobile_confidence_score = (
                mobile_diagnosis_input.mobile_confidence_score
            )
            db.commit()
            return DiagnosisOutputSchema.model_validate(uploaded_diagnosis)

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
