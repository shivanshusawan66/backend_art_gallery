import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from django.utils import timezone
from ai_mf_backend.api_application import application

# ================== Constants ==================
FORGOT_PASSWORD_URL = "/api/v1/forgot_password"
CHANGE_PASSWORD_URL = "/api/v1/change_password"
RESEND_OTP_URL = "/api/v1/resend_otp"  # Assuming you have a URL for OTP resending


# ================== Fixtures ==================
@pytest.fixture
def client():
    """Returns a TestClient instance for making requests to the FastAPI application."""
    return TestClient(application)


@pytest.fixture
def mock_now():
    """Mocks the current time to a fixed datetime for consistent testing."""
    current_time = datetime(2024, 1, 1, 12, 0, 0)
    with patch("django.utils.timezone.now", return_value=current_time):
        yield current_time


@pytest.fixture
def mock_jwt_token():
    """Creates a valid JWT token payload"""
    current_time = timezone.now()
    return {
        "email": "test@example.com",
        "token_type": "login",
        "creation_time": current_time.timestamp(),
        "expiry": (current_time + timedelta(hours=1)).timestamp(),
    }


@pytest.fixture
def mock_user():
    """Creates a mock user object for testing."""
    user = MagicMock()
    user.email = "test@example.com"
    user.user_id = 2
    user.password = "hashed_password"
    user.mobile_number = None
    return user


@pytest.fixture
def mock_mobile_user():
    """Creates a mock user object with a mobile number for testing."""
    user = MagicMock()
    user.email = None
    user.user_id = 2
    user.password = "hashed_password"
    user.mobile_number = "1234567890"
    return user


@pytest.fixture
def mock_otp_doc(mock_now):
    """Creates a mock OTP document for testing."""
    otp_doc = MagicMock()
    otp_doc.update_date = mock_now - timedelta(minutes=1)
    otp_doc.otp = "123456"
    otp_doc.otp_valid = mock_now + timedelta(minutes=15)
    return otp_doc


# ================== Helper Functions ==================
def setup_forgot_password_mocks(
    mock_user_contact,
    mock_otp_logs,
    mock_jwt,
    mock_otp,
    mock_throttle,
    mock_otp_save,
    mock_otp_doc,
    user,
):
    mock_user_contact.filter.return_value.first.return_value = user
    mock_jwt.return_value = "mock_jwt_token"
    mock_otp.return_value = "123456"
    mock_throttle.return_value = (True, None)
    mock_otp_save.return_value = None
    mock_otp_logs.filter.return_value.first.return_value = mock_otp_doc


# ================== Forgot Password Tests ==================
@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
@patch("ai_mf_backend.models.v1.database.user.OTPlogs.objects")
@patch("ai_mf_backend.utils.v1.authentication.secrets.jwt_token_checker")
@patch("ai_mf_backend.utils.v1.authentication.otp.send_otp")
@patch("ai_mf_backend.utils.v1.authentication.rate_limiting.throttle_otp_requests")
@patch("ai_mf_backend.models.v1.database.user.OTPlogs.save")
def test_forgot_password_success_email(
    mock_otp_save,
    mock_throttle,
    mock_otp,
    mock_jwt,
    mock_otp_logs,
    mock_user_contact,
    client,
    mock_now,
    mock_user,
    mock_otp_doc,
):
    # Arrange
    setup_forgot_password_mocks(
        mock_user_contact,
        mock_otp_logs,
        mock_jwt,
        mock_otp,
        mock_throttle,
        mock_otp_save,
        mock_otp_doc,
        mock_user,
    )

    request_data = {"email": "test@example.com", "mobile_no": None}

    # Act
    response = client.post(FORGOT_PASSWORD_URL, json=request_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert "token" in response.json()["data"]
    assert "otp" in response.json()["data"]


@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
@patch("ai_mf_backend.models.v1.database.user.OTPlogs.objects")
@patch("ai_mf_backend.utils.v1.authentication.secrets.jwt_token_checker")
@patch("ai_mf_backend.utils.v1.authentication.otp.send_otp")
@patch("ai_mf_backend.utils.v1.authentication.rate_limiting.throttle_otp_requests")
@patch("ai_mf_backend.models.v1.database.user.OTPlogs.save")
def test_forgot_password_success_mobile(
    mock_otp_save,
    mock_throttle,
    mock_otp,
    mock_jwt,
    mock_otp_logs,
    mock_user_contact,
    client,
    mock_now,
    mock_mobile_user,
    mock_otp_doc,
):
    # Arrange
    setup_forgot_password_mocks(
        mock_user_contact,
        mock_otp_logs,
        mock_jwt,
        mock_otp,
        mock_throttle,
        mock_otp_save,
        mock_otp_doc,
        mock_mobile_user,
    )

    request_data = {"email": None, "mobile_no": "1234567890"}

    # Act
    response = client.post(FORGOT_PASSWORD_URL, json=request_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert "token" in response.json()["data"]
    assert "otp" in response.json()["data"]


@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
def test_forgot_password_user_not_found(mock_user_contact, client):
    # Arrange
    mock_user_contact.filter.return_value.first.return_value = None

    request_data = {"email": "nonexistent@example.com", "mobile_no": None}

    # Act
    response = client.post(FORGOT_PASSWORD_URL, json=request_data)

    # Assert
    assert response.status_code == 404
    assert response.json()["status"] is False
    assert "This user does not exist" in response.json()["message"]


@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
def test_forgot_password_no_password_set(mock_user_contact, client, mock_user):
    # Arrange
    mock_user.password = None
    mock_user_contact.filter.return_value.first.return_value = mock_user

    request_data = {"email": "test@example.com", "mobile_no": None}

    # Act
    response = client.post(FORGOT_PASSWORD_URL, json=request_data)

    # Assert
    assert response.status_code == 401
    assert response.json()["status"] is False
    assert "Please login using OTP" in response.json()["message"]


@pytest.mark.parametrize(
    "request_data,expected_status_code,expected_message",
    [
        (
            {"email": None, "mobile_no": None},
            400,
            "Either one of email or mobile number is required to proceed with this request",
        ),
        (
            {"email": "test@example.com", "mobile_no": "9876543210"},
            400,
            "Both Mobile and email cannot be processed at the same time",
        ),
        ({"email": "invalid_email", "mobile_no": None}, 422, "Bad Email provided:"),
        (
            {"email": None, "mobile_no": "invalid_phone"},
            422,
            "Bad phone number provided:",
        ),
    ],
)
def test_forgot_password_validation_errors(
    request_data, expected_status_code, expected_message, client
):
    # Act
    response = client.post(FORGOT_PASSWORD_URL, json=request_data)

    # Assert
    assert response.status_code == expected_status_code
    assert expected_message in response.json()["message"]
    assert response.json()["status"] is False


@pytest.mark.parametrize(
    "request_data,expected_status_code,expected_message",
    [
        (
            {"old_password": "correct_old_password", "new_password": ""},
            422,
            "This request cannot proceed without a new password being provided",
        ),
        (
            {"old_password": "correct_old_password", "new_password": "weak"},
            422,
            "Bad Password provided:",
        ),
    ],
)
@patch("ai_mf_backend.utils.v1.authentication.secrets.jwt_token_checker")
@patch("ai_mf_backend.utils.v1.authentication.secrets.password_checker")
@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
def test_change_password_validation_errors(
    mock_user_contact,
    mock_password_checker,
    mock_jwt_checker,
    request_data,
    expected_status_code,
    expected_message,
    client,
    mock_user,
    mock_jwt_token,
):
    # Setup mocks
    mock_user_contact.filter.return_value.first.return_value = mock_user
    mock_jwt_checker.return_value = mock_jwt_token
    mock_password_checker.return_value = True

    response = client.post(
        CHANGE_PASSWORD_URL,
        json=request_data,
        headers={"Authorization": "Bearer mock_token"},
    )

    assert response.status_code == expected_status_code
    assert response.json()["status"] is False
    assert expected_message in response.json()["message"]


# ================== Resend OTP Tests ==================
@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
@pytest.mark.parametrize(
    "request_data,expected_status_code,expected_message",
    [
        (
            {"email": None, "mobile_no": None},
            400,
            "Either one of email or mobile number is required to proceed with this request",
        ),
        (
            {"email": "test@example.com", "mobile_no": "9876543210"},
            400,
            "Both Mobile and email cannot be processed at the same time",
        ),
    ],
)
def test_resend_otp_validation_errors(
    mock_user_contact, request_data, expected_status_code, expected_message, client
):
    # Act
    response = client.post(RESEND_OTP_URL, json=request_data)

    # Assert
    assert response.status_code == expected_status_code
    assert expected_message in response.json()["message"]
    assert response.json()["status"] is False
