# import logging
# from datetime import datetime, timedelta
# from django.utils import timezone
# from fastapi import APIRouter, Response
# from asgiref.sync import sync_to_async
# from fastapi import Header, Request
# from typing import Annotated
# from app.schemas.v1.authentication import (
#     ForgotPasswordRequest,
#     ForgotPasswordResponse,
#     ChangePasswordRequest,
#     ChangePasswordResponse,
# )
# from app.models import UserManagement
# from utils.v1.authentication.otp import send_email_otp
# from utils.v1.authentication.secrets import (
#     jwt_token_checker,
#     password_encoder,
#     login_checker,
#     password_checker,
# )

# logger = logging.getLogger(__name__)

# router = APIRouter()


# @router.post("/forgot_password", response_model=ForgotPasswordResponse, status_code=200)
# async def forgot_password(request: ForgotPasswordRequest):
#     """
#     Handles the forgot password functionality by generating an OTP and sending it to the user's
#     email or mobile number. A JWT token is also generated, which is used for resetting the password.

#     This endpoint supports two modes of identity verification:
#     1. Through email.
#     2. Through mobile number.

#     If the user exists in the system, an OTP will be generated and sent to the provided email or mobile number,
#     and a JWT token will be created to facilitate the password reset process. If the user does not exist,
#     an error response will be returned.

#     Parameters:
#     -----------
#     request : ForgotPasswordRequest
#         A Pydantic model instance containing the user's email or mobile number for initiating the password reset 
#         process.

#     Logic:
#     ------
#     1. **Email-based flow**:
#        - If an email is provided, the system checks whether the user exists with that email.
#        - If the user exists, an OTP is generated, valid for 15 minutes, and a JWT token is created with a 7-day expiry.
#        - The OTP is sent via email and stored in the user's record, and the JWT token is returned in the response.
#        - If the user does not exist, a `404 Not Found` response is returned.

#     2. **Mobile number-based flow**:
#        - If a mobile number is provided, the system checks whether the user exists with that mobile number.
#        - Similar to the email flow, an OTP is generated and a JWT token is created.
#        - The OTP is sent via the mobile number (via SMS or other channels), and the JWT token is returned in the response.
#        - If the user does not exist, a `404 Not Found` response is returned.

#     Returns:
#     --------
#     ForgotPasswordResponse: JSON
#         A structured response indicating the success or failure of the forgot password request.
#         On success, an OTP is sent to the provided email or mobile number, and a JWT token is generated for password reset.

#     Possible Status Codes:
#     ----------------------
#     - 200: OTP successfully sent and JWT token generated.
#     - 404: User does not exist for the provided email or mobile number.

#     Example:
#     --------
#     **Email-based Request**:
#     Request:
#         POST /forgot_password
#         {
#             "email": "user@example.com"
#         }

#     Response:
#         {
#             "status": true,
#             "message": "OTP has been sent to user@example.com. Please check.",
#             "data": {
#                 "token": "jwt_token",
#                 "userdata": {
#                     "email": "user@example.com"
#                 }
#             }
#         }

#     **Mobile number-based Request**:
#     Request:
#         POST /forgot_password
#         {
#             "mobile_no": "+1234567890"
#         }

#     Response:
#         {
#             "status": true,
#             "message": "OTP has been sent to +1234567890. Please check.",
#             "data": {
#                 "token": "jwt_token",
#                 "userdata": {
#                     "mobile_no": "+1234567890"
#                 }
#             }
#         }
#     """
#     if request.email:
#         user_doc = await sync_to_async(
#             UserManagement.objects.filter(email=request.email).first
#         )()

#         if user_doc:
#             otp = send_email_otp()
#             current_time = timezone.now()

#             payload = {
#                 "email": request.email,
#                 "token_type": "forgot_password",
#                 "creation_time": current_time.timestamp(),
#                 "expiry": (current_time + timedelta(days=7)).timestamp(),
#             }

#             jwt_token = jwt_token_checker(payload=payload, encode=True)

#             user_doc.otp = otp
#             user_doc.otp_valid_till = current_time + timedelta(minutes=15)
#             await sync_to_async(user_doc.save)()

#             return ForgotPasswordResponse(
#                 status=True,
#                 message=f"OTP has been sent to {request.email}. Please check.",
#                 data={"token": jwt_token, "userdata": {"email": request.email}},
#             )
#         else:
#             return ForgotPasswordResponse(
#                 status=False,
#                 message=f"This profile does not exist. {request.email}",
#                 data={"error": "This profile does not exist."},
#                 status_code=404,
#             )
#     elif request.mobile_no:
#         user_doc = await sync_to_async(
#             UserManagement.objects.filter(mobile_numner=request.mobile_no).first
#         )()

#         if user_doc:
#             otp = send_email_otp()
#             current_time = timezone.now()

#             payload = {
#                 "mobile_no": request.mobile_no,
#                 "token_type": "forgot_password",
#                 "creation_time": current_time.timestamp(),
#                 "expiry": (current_time + timedelta(days=7)).timestamp(),
#             }

#             jwt_token = jwt_token_checker(payload=payload, encode=True)

#             user_doc.otp = otp
#             user_doc.otp_valid_till = current_time + timedelta(minutes=15)
#             await sync_to_async(user_doc.save)()

#             return ForgotPasswordResponse(
#                 status=True,
#                 message=f"OTP has been sent to {request.mobile_no}. Please check.",
#                 data={"token": jwt_token, "userdata": {"email": request.mobile_no}, "otp":otp},
#             )
#         else:
#             return ForgotPasswordResponse(
#                 status=False,
#                 message=f"This profile does not exist. {request.mobile_no}",
#                 data={"error": "This profile does not exist."},
#                 status_code=404,
#             )


# @router.post("/change_password", response_model=ChangePasswordResponse, status_code=200)
# async def change_password(request: ChangePasswordRequest):
#     """
#     Handles the password change process for users, allowing them to reset their password
#     after verifying their old password. This function supports password changes for both email and
#     mobile number-based profiles, utilizing a JWT token for authentication.

#     Parameters:
#     -----------
#     request : ChangePasswordRequest
#         A Pydantic model instance containing the user's old password, new password, and JWT token
#         for verifying the user.

#     Logic:
#     ------
#     1. **Token Verification**:
#        - The function first checks the validity of the provided JWT token using the `login_checker` function.
#        - If the token is valid, it is decoded to extract either the user's email or mobile number from the payload.

#     2. **Email-based Profile**:
#        - If the token contains an email, the function retrieves the user associated with that email.
#        - If the user exists, it verifies the old password against the stored password.
#        - If the old password matches, the new password is encoded and saved, and the password change is confirmed with a success message.
#        - If the old password does not match, a 403 error is returned, indicating that the provided old password was incorrect.

#     3. **Mobile number-based Profile**:
#        - If the token contains a mobile number, the function retrieves the user associated with that mobile number.
#        - Similar to the email flow, the old password is verified, and upon a match, the new password is saved.
#        - If the old password is incorrect, a failure response is returned.

#     Returns:
#     --------
#     ChangePasswordResponse: JSON
#         A structured response indicating the success or failure of the password change request.
#         On success, the password is updated, and a confirmation message is returned.
#         On failure, the response includes an error message.

#     Possible Status Codes:
#     ----------------------
#     - 200: Password changed successfully.
#     - 403: Old password does not match, and password update fails.
#     - 404: User profile does not exist for the provided email or mobile number.

#     Example:
#     --------
#     **Email-based Request**:
#     Request:
#         POST /change_password
#         {
#             "old_password": "old_password123",
#             "password": "new_password456",
#             "token": "valid_jwt_token"
#         }

#     Response:
#         {
#             "status": true,
#             "message": "Your password has been reset successfully!",
#             "data": {}
#         }

#     **Mobile number-based Request**:
#     Request:
#         POST /change_password
#         {
#             "old_password": "old_password123",
#             "password": "new_password456",
#             "token": "valid_jwt_token"
#         }

#     Response:
#         {
#             "status": true,
#             "message": "Your password has been reset successfully!",
#             "data": {}
#         }

#     **Failure Response (Incorrect Old Password)**:
#     Response:
#         {
#             "status": false,
#             "message": "Password update failed",
#             "data": {
#                 "error": "Old Password didn't match. Please provide the correct Old Password."
#             },
#             "status_code": 403
#         }
#     """
#     jwt_token = await login_checker(request.token)
#     decoded_payload = jwt_token_checker(jwt_token=jwt_token, encode=False)
#     if "email" in decoded_payload:
#         user_doc = await sync_to_async(
#             UserManagement.objects.filter(email=decoded_payload["email"]).first
#         )()
#         if user_doc is None:
#             return ChangePasswordResponse(
#                 status=False,
#                 message="This profile does not exist.",
#                 data={"error": "This profile does not exist."},
#             )
#         if password_checker(request.old_password, user_doc.password):
#             user_doc.password = password_encoder(request.password)
#             user_doc.updated_at = timezone.now()
#             await sync_to_async(user_doc.save)()
#             return ChangePasswordResponse(
#                 status=True,
#                 message="Your password has been reset successfully!",
#                 data={},
#             )
#         else:
#             return ChangePasswordResponse(
#                 status=False,
#                 message="Password update failed",
#                 data={
#                     "error": "Old Password didn't match. Please provide the correct Old Password."
#                 },
#                 status_code=403,
#             )
#     elif "mobile_no" in decoded_payload:
#         user_doc = await sync_to_async(
#             UserManagement.objects.filter(
#                 mobile_number=decoded_payload["mobile_no"]
#             ).first
#         )()
#         print(user_doc)
#         if user_doc is None:
#             return ChangePasswordResponse(
#                 status=False,
#                 message="This profile does not exist.",
#                 data={"error": "This profile does not exist."},
#             )
#         if password_checker(request.old_password, user_doc.password):
#             user_doc.password = password_encoder(request.password)
#             user_doc.updated_at = timezone.now()
#             await sync_to_async(user_doc.save)()
#             return ChangePasswordResponse(
#                 status=True,
#                 message="Your password has been reset successfully!",
#                 data={},
#             )
#         else:
#             return ChangePasswordResponse(
#                 status=False,
#                 message="Password update failed",
#                 data={"error": "Old Password didn't match. Please provide the correct"},
#             )
