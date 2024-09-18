import random
import logging
import smtplib
from email.mime.text import MIMEText
import os

logger=logging.getLogger(__name__)
def send_email_otp(receiver_email_id: str = None) -> int:
    """
    This method generates an OTP and sends it to the provided email address.
    :param receiver_email_id: email address of the person we want to send email to
    :return: otp a random 6 digit integer as otp
    """
    
    otp = random.randint(100000, 999999)

    # Replace these with your email configuration
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "OTP Verification"
    msg["From"] = sender_email
    msg["To"] = receiver_email_id

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            logger.info(f"OTP sent to {receiver_email_id}")
            return otp  # Return OTP on success
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP Authentication Error: Check your email and password.")
        print("Error sending OTP: SMTP Authentication Error.")
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        print(f"Error sending OTP: {e}")
    
    return otp


def send_email_otp_verification_done(receiver_email_id: str = None) -> None:
    """
    This method sends a confirmation email to the user after their OTP verification is successful.
    :param receiver_email_id: email address of the person we want to send email to
    :return:
    """

    # Replace these with your email configuration
    sender_email = "sahilgarg2814@gmail.com"
    sender_password = "sahil9896"

    msg = MIMEText("Your OTP verification was successful. You can now proceed to log in.")
    msg["Subject"] = "OTP Verification Successful"
    msg["From"] = sender_email
    msg["To"] = receiver_email_id

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            logger.info(f"OTP verification confirmation sent to {receiver_email_id}")
    except Exception as e:
        logger.error(f"Error sending OTP verification confirmation: {e}")