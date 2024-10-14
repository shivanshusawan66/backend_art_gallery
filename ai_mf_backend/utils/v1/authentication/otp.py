import random
import logging
import smtplib
from email.mime.text import MIMEText
import os

logger = logging.getLogger(__name__)


def send_email_otp() -> int:
    """
    This method generates an OTP and sends it to the provided email address.
    :param receiver_email_id: email address of the person we want to send email to
    :return: otp a random 6 digit integer as otp
    """

    otp = random.randint(100000, 999999)
    return otp


def send_email_otp_verification_done(receiver_email_id: str = None) -> None:
    """
    This method sends a confirmation email to the user after their OTP verification is successful.
    :param receiver_email_id: email address of the person we want to send email to
    :return:
    """