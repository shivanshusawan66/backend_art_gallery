import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from ai_mf_backend.api_application import application


# Create a fixture for the test client
@pytest.fixture
def client():
    return TestClient(application)


# Mock timezone.now() for consistent testing
@pytest.fixture
def mock_now():
    current_time = datetime(2024, 1, 1, 12, 0, 0)
    with patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = current_time
        yield current_time


# Tests for POST /password_user_auth endpoint
@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
@patch("ai_mf_backend.utils.v1.authentication.secrets.jwt_token_checker")
@patch("ai_mf_backend.utils.v1.authentication.secrets.password_checker")
@patch("ai_mf_backend.models.v1.database.user_authentication.UserLogs.save")
def test_password_auth_success_existing_user(
    mock_save, mock_pass_check, mock_jwt, mock_user_contact, client, mock_now
):
    # Arrange
    email = "test@example.com"
    password = "TestPass123!"

    # Generate a valid hashed password
    hashed_password = make_password(password)

    mock_user = MagicMock()
    mock_user.email = email
    mock_user.password = hashed_password  # Set hashed password
    mock_user.is_verified = True
    mock_user.user_id = 1

    mock_user_contact.filter.return_value.first.return_value = mock_user
    mock_jwt.return_value = "test_token"

    # Ensure password_checker compares correctly
    mock_pass_check.side_effect = (
        lambda provided_password, stored_password: check_password(
            provided_password, stored_password
        )
    )

    mock_save.return_value = None

    request_data = {
        "email": email,
        "password": password,
        "mobile_no": None,
        "remember_me": False,
        "ip_details": {},
        "device_type": "web",
    }

    # Act
    response = client.post("/api/v1/password_user_auth", json=request_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] is True
    assert response.json()["data"]["token"] == "test_token"


@pytest.mark.parametrize(
    "request_data,expected_status_code,expected_message",
    [
        (
            {"email": None, "mobile_no": None, "password": "TestPass123!"},
            400,
            "Either one of email or mobile number is required to proceed with this request.",
        ),
        (
            {
                "email": "test@example.com",
                "mobile_no": "+919876543210",
                "password": "TestPass123!",
            },
            400,
            "Both Mobile and email cannot be processed at the same time.",
        ),
        (
            {"email": "invalid_email", "mobile_no": None, "password": "TestPass123!"},
            422,
            "Bad Email provided:",
        ),
        (
            {"email": None, "mobile_no": "invalid_phone", "password": "TestPass123!"},
            422,
            "Bad phone number provided:",
        ),
    ],
)
@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
def test_password_auth_validation_errors(
    mock_user_contact, request_data, expected_status_code, expected_message, client
):
    # Arrange
    mock_user_contact.filter.return_value.first.return_value = None

    # Act
    response = client.post("/api/v1/password_user_auth", json=request_data)

    # Assert
    assert response.status_code == expected_status_code
    assert expected_message in response.json()["message"]


@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
@patch("ai_mf_backend.utils.v1.authentication.secrets.jwt_token_checker")
@patch("ai_mf_backend.utils.v1.authentication.otp.send_otp")
@patch("ai_mf_backend.utils.v1.authentication.secrets.password_encoder")
@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.save")
@patch("ai_mf_backend.models.v1.database.user.OTPlogs.save")
@patch("ai_mf_backend.models.v1.database.user_authentication.UserLogs.save")
def test_password_auth_new_user_signup(
    mock_user_logs_save,
    mock_otp_save,
    mock_user_save,
    mock_pass_encode,
    mock_otp,
    mock_jwt,
    mock_user_contact,
    client,
    mock_now,
):
    # Arrange
    email = "new@example.com"
    password = "TestPass123!"

    mock_user_contact.filter.return_value.first.return_value = None
    mock_jwt.return_value = "test_token"
    mock_otp.return_value = "123456"
    mock_pass_encode.return_value = "hashed_password"
    mock_user_save.return_value = None
    mock_otp_save.return_value = None
    mock_user_logs_save.return_value = None

    request_data = {
        "email": email,
        "password": password,
        "mobile_no": None,
        "remember_me": False,
        "ip_details": {},
        "device_type": "web",
    }

    # Act
    response = client.post("/api/v1/password_user_auth", json=request_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["status"] is True
    assert "token" in response.json()["data"]
    assert "otp" in response.json()["data"]


# Tests for POST /otp_user_auth endpoint
@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
@patch("ai_mf_backend.models.v1.database.user.OTPlogs.objects")
@patch("ai_mf_backend.utils.v1.authentication.secrets.jwt_token_checker")
@patch("ai_mf_backend.utils.v1.authentication.otp.send_otp")
@patch("ai_mf_backend.utils.v1.authentication.rate_limiting.throttle_otp_requests")
@patch("ai_mf_backend.models.v1.database.user.OTPlogs.save")
def test_otp_auth_success_existing_user(
    mock_otp_save,
    mock_throttle,
    mock_otp,
    mock_jwt,
    mock_otp_logs,
    mock_user_contact,
    client,
    mock_now,
):
    # Arrange
    email = "test@example.com"

    mock_user = MagicMock()
    mock_user.email = email
    mock_user.user_id = 1

    mock_user_contact.filter.return_value.first.return_value = mock_user
    mock_jwt.return_value = "test_token"
    mock_otp.return_value = "123456"
    mock_throttle.return_value = (True, None)
    mock_otp_save.return_value = None

    mock_otp_doc = MagicMock()
    mock_otp_doc.update_date = mock_now - timedelta(minutes=1)
    mock_otp_logs.filter.return_value.first.return_value = mock_otp_doc

    request_data = {"email": email, "mobile_no": None}

    # Act
    response = client.post("/api/v1/otp_user_auth", json=request_data)

    # Assert
    assert response.status_code == 202
    assert response.json()["status"] is True
    assert "token" in response.json()["data"]["data"]
    assert "otp" in response.json()["data"]


@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.objects")
@patch("ai_mf_backend.utils.v1.authentication.secrets.jwt_token_checker")
@patch("ai_mf_backend.utils.v1.authentication.otp.send_otp")
@patch("ai_mf_backend.models.v1.database.user.UserContactInfo.save")
@patch("ai_mf_backend.models.v1.database.user.OTPlogs.save")
def test_otp_auth_new_user_signup(
    mock_otp_save, mock_user_save, mock_otp, mock_jwt, mock_user_contact, client
):
    # Arrange
    email = "new@example.com"

    mock_user_contact.filter.return_value.first.return_value = None
    mock_jwt.return_value = "test_token"
    mock_otp.return_value = "123456"
    mock_user_save.return_value = None
    mock_otp_save.return_value = None

    request_data = {"email": email, "mobile_no": None}

    # Act
    response = client.post("/api/v1/otp_user_auth", json=request_data)

    # Assert
    assert response.status_code == 202
    assert response.json()["status"] is True
    assert "token" in response.json()["data"]["data"]
    assert "otp" in response.json()["data"]


@pytest.mark.parametrize(
    "request_data,expected_status_code,expected_message",
    [
        (
            {"email": None, "mobile_no": None},
            400,
            "Either one of email or mobile number is required to proceed with this request.",
        ),
        (
            {"email": "test@example.com", "mobile_no": "+919876543210"},
            400,
            "Both Mobile and email cannot be processed at the same time.",
        ),
        ({"email": "invalid_email", "mobile_no": None}, 422, "Bad Email provided:"),
        (
            {"email": None, "mobile_no": "invalid_phone"},
            422,
            "Bad phone number provided:",
        ),
    ],
)
def test_otp_auth_validation_errors(
    request_data, expected_status_code, expected_message, client
):
    # Act
    response = client.post("/api/v1/otp_user_auth", json=request_data)

    # Assert
    assert response.status_code == expected_status_code
    assert expected_message in response.json()["message"]
