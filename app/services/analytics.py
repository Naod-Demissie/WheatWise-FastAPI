import os
from io import BytesIO
from fastapi import HTTPException
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from fastapi import status

from sqlalchemy.orm import Session
from sqlalchemy import inspect, text, func

from scikitplot.metrics import plot_confusion_matrix
from sklearn.metrics import confusion_matrix

from app.models.diagnosis import DiagnosisModel
from app.models.enums import DiseaseTypeEnum
from app.utils.session import engine
from app.schemas.user import UserOutputSchema


load_dotenv()


class AnalyticsServices:
    @staticmethod
    async def get_diagnosis_report(
        db: Session,
        current_user: UserOutputSchema,
        return_json: bool,
    ) -> BytesIO | dict:
        """
        Get a confusion matrix plot for the diagnoses on the database.

        Args:
            db (Session): The database session.
            current_user (UserOutputSchema): Current user data
            return_json (bool): If True, return the confusion matrix report as a JSON object.
                                If False, return the confusion matrix plot as a BytesIO object.

        Returns:
            BytesIO | dict: If return_json is True, a dictionary containing the confusion matrix report.
                            If return_json is False, a BytesIO object containing the image data of the confusion matrix plot.
        """
        try:
            print(f"{current_user.role=}")
            print(f"{ current_user.role != 'System Admin'}")
            if current_user.role != "System Admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only system admin can access this endpoint.",
                )

            diagnoses = (
                db.query(DiagnosisModel)
                .filter(
                    DiagnosisModel.server_diagnosis.isnot(None)
                    & DiagnosisModel.manual_diagnosis.isnot(None)
                )
                .all()
            )

            server_diagnoses = [
                diagnosis.server_diagnosis.value for diagnosis in diagnoses
            ]
            manual_diagnoses = [
                diagnosis.manual_diagnosis.value for diagnosis in diagnoses
            ]
            labels = [type.value for type in DiseaseTypeEnum]

            if return_json:
                cm = confusion_matrix(manual_diagnoses, server_diagnoses, labels=labels)
                cm = cm.tolist()

                correct_predictions = sum([cm[i][i] for i in range(len(labels))])
                total = sum(
                    [cm[i][j] for i in range(len(labels)) for j in range(len(labels))]
                )
                incorrect_predictions = total - correct_predictions
                cm_dict = {}
                for i, actual_class in enumerate(labels):
                    cm_dict[f"Actual {actual_class}"] = {}
                    for j, predicted_class in enumerate(labels):
                        cm_dict[f"Actual {actual_class}"][
                            f"Predicted {predicted_class}"
                        ] = cm[i][j]

                return {
                    "correct_predictions": correct_predictions,
                    "incorrect_predictions": incorrect_predictions,
                    "total": total,
                    "confusion_matrix": cm_dict,
                }
            else:
                plt.figure()
                plot_confusion_matrix(
                    manual_diagnoses,
                    server_diagnoses,
                    labels,
                    cmap=plt.cm.Blues,
                    figsize=(7, 7),
                )

                plt.xlabel("Manual Diagnosis")
                plt.ylabel("Server Diagnosis")
                plt.title("Diagnosis Confusion Matrix")
                plt.tight_layout()

                # Convert plot to BytesIO object
                image_stream = BytesIO()
                plt.savefig(image_stream, format="png")
                plt.close()
                image_stream.seek(0)

                return image_stream
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    @staticmethod
    async def get_system_report(db: Session, current_user: UserOutputSchema) -> dict:
        """
        Get a report of the system including sizes of the database table and upload files.

        Args:
            db (Session): The database session.
            current_user (UserOutputSchema): Current user data

        Returns:
            dict: A dictionary containing the database and uploaded file report.
        """
        try:
            if current_user.role != "System Admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only system admin can access this endpoint.",
                )

            inspector = inspect(engine)
            table_names = inspector.get_table_names()

            table_sizes = {}
            for table_name in table_names:
                row_count = db.execute(
                    text(f"SELECT COUNT(*) FROM {table_name};")
                ).scalar()

                db_size = db.execute(
                    func.pg_size_pretty(func.pg_total_relation_size(table_name))
                ).scalar()
                db_size_mb = round(float(db_size.split()[0]) / 1024, 2)

                table_sizes[table_name] = {
                    "row counts": row_count,
                    "size(MB)": db_size_mb,
                }

            upload_folder_path = os.getenv("UPLOAD_FOLDER_PATH")
            upload_report = {}
            if upload_folder_path:
                uploaded_files = os.listdir(upload_folder_path)
                total_files = len(uploaded_files)
                total_size = sum(
                    os.path.getsize(os.path.join(upload_folder_path, f))
                    for f in uploaded_files
                )
                total_size = round(total_size / (1024 * 1024), 2)
                upload_report = {
                    "total_files": total_files,
                    "total_size(MB)": total_size,
                }

            return {"Database Report": table_sizes, "Upload Report": upload_report}
        except Exception as e:
            print(e)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
