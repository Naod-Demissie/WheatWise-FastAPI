import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

OTP_EMAIL_PASSWORD = os.getenv("OTP_EMAIL_PASSWORD")


def send_otp(sender_email, receiver_email, otp):
    """
    Send an email with the OTP (One-Time Password) for password reset.

    Args:
        sender_email (str): Sender's email address
        receiver_email (str): Receiver's email address
        otp (str): One-Time Password (OTP) to be sent

    Returns:
        None
    """

    subject = "Password Reset OTP"
    body = f"""
    You recently requested to reset your password for your account. Please use the following OTP (One-Time Password) to complete the password reset process:

    OTP: {otp}

    Please enter this OTP on the password reset page within the next 24 hours. If you did not request a password reset, please ignore this email.

    Thank you,
    Ethiopian Artificial Intelligence Support Team

    """
    em = EmailMessage()
    em["From"] = sender_email
    em["To"] = receiver_email
    em["Subject"] = subject
    em.set_content(body)

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(sender_email, OTP_EMAIL_PASSWORD)
        smtp.sendmail(sender_email, receiver_email, em.as_string())
