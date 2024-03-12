import schedule
import time

from app.services.diagnosis import DiagnosisServices


def run_routine_diagnoses():
    """
    Schedule routine diagnoses to run every hour.
    """
    # Schedule the method to run every hour
    schedule.every().hour.do(lambda: DiagnosisServices.batch_diagnose_uploaded_images())
    while True:
        schedule.run_pending()
        time.sleep(10)  # sleep to avoid CPU consumption
