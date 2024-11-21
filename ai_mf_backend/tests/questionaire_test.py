import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from asgiref.sync import sync_to_async

from django.db import DatabaseError

from ai_mf_backend.api_application import application


# Constants
SECTIONS_URL = "/api/v1/sections"
SECTION_QUESTIONS_URL = "/api/v1/section-wise-questions"

@pytest.fixture
def client():
    """Returns a TestClient instance for making requests to the FastAPI application."""
    return TestClient(application)

@pytest.fixture
def mock_login_token():
    """Creates a mock login token for authorization testing."""
    return {
        "Authorization": "Bearer mock_valid_token"
    }

# ================== Sections Endpoint Tests ==================
@pytest.mark.asyncio
async def test_get_sections_success(client, mock_login_token):
    """
    Test successful retrieval of sections
    """
    with (
        patch("ai_mf_backend.models.v1.database.questions.Section.objects.all") as mock_sections,
        patch("ai_mf_backend.utils.v1.authentication.secrets.login_checker", return_value=True)
    ):
        # Create mock sections
        mock_section1 = MagicMock(pk=1, section='Section 1')
        mock_section2 = MagicMock(pk=2, section='Section 2')
        
        mock_sections.return_value = [mock_section1, mock_section2]

        # Act
        response = client.get(SECTIONS_URL, headers=mock_login_token)

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["status"] is True
        assert response_data["message"] == "Sections fetched successfully."
        assert len(response_data["data"]) == 2
        
        # Check section details
        assert response_data["data"][0]["section_id"] == 1
        assert response_data["data"][0]["section_name"] == "Section 1"

@pytest.mark.asyncio
async def test_get_sections_database_error(client, mock_login_token):
    """
    Test sections endpoint when a database error occurs
    """
    with (
        patch("ai_mf_backend.models.v1.database.questions.Section.objects.all", side_effect=DatabaseError) as mock_sections,
        patch("ai_mf_backend.utils.v1.authentication.secrets.login_checker", return_value=True)
    ):
        # Act
        response = client.get(SECTIONS_URL, headers=mock_login_token)

        # Assert
        assert response.status_code == 500
        response_data = response.json()
        
        assert response_data["status"] is False
        assert response_data["message"] == "Failed to fetch sections."

# ================== Section Questions Endpoint Tests ==================
@pytest.mark.asyncio
async def test_section_questions_success(client, mock_login_token):
    """
    Test successful retrieval of section-wise questions
    """
    with (
        patch("ai_mf_backend.models.v1.database.questions.Section.objects.filter") as mock_section_filter,
        patch("ai_mf_backend.models.v1.database.questions.Question.objects.filter") as mock_questions_filter,
        patch("ai_mf_backend.models.v1.database.questions.Allowed_Response.objects.filter") as mock_responses_filter,
        patch("ai_mf_backend.models.v1.database.questions.ConditionalQuestion.objects.filter") as mock_conditional_filter,
        patch("ai_mf_backend.utils.v1.authentication.secrets.login_checker", return_value=True)
    ):
        # Mock Section
        mock_section = MagicMock(pk=1, section='Test Section')
        mock_section_filter.return_value.first.return_value = mock_section

        # Mock Questions
        mock_question1 = MagicMock(pk=1, question='Question 1')
        mock_questions_filter.return_value = [mock_question1]

        # Mock Responses
        mock_responses_filter.return_value.values.return_value = [
            {"id": 1, "response": "Option 1"},
            {"id": 2, "response": "Option 2"}
        ]

        # Mock Conditional Questions
        mock_conditional_filter.return_value.values.return_value = []

        # Act
        request_data = {"section_id": 1}
        response = client.post(SECTION_QUESTIONS_URL, 
                               json=request_data, 
                               headers=mock_login_token)

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["status"] is True
        assert response_data["message"] == "Successfully fetched section wise questions and responses"
        assert response_data["data"]["section_id"] == 1
        assert response_data["data"]["section_name"] == "Test Section"

@pytest.mark.parametrize("invalid_section_id", [None, "invalid", -1, 0])
@pytest.mark.asyncio
async def test_section_questions_invalid_section_id(client, mock_login_token, invalid_section_id):
    """
    Test section questions endpoint with invalid section ID
    """
    request_data = {"section_id": invalid_section_id}
    response = client.post(SECTION_QUESTIONS_URL, 
                           json=request_data, 
                           headers=mock_login_token)

    # Assert
    assert response.status_code == 422
    response_data = response.json()
    
    assert response_data["status"] is False
    assert "section_id" in response_data["message"].lower()

@pytest.mark.asyncio
async def test_section_questions_section_not_found(client, mock_login_token):
    """
    Test section questions endpoint when section is not found
    """
    with (
        patch("ai_mf_backend.models.v1.database.questions.Section.objects.filter") as mock_section_filter,
        patch("ai_mf_backend.utils.v1.authentication.secrets.login_checker", return_value=True)
    ):
        # Mock no section found
        mock_section_filter.return_value.first.return_value = None

        # Act
        request_data = {"section_id": 999}
        response = client.post(SECTION_QUESTIONS_URL, 
                               json=request_data, 
                               headers=mock_login_token)

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        
        assert response_data["status"] is False
        assert response_data["message"] == "Section not found."

@pytest.mark.asyncio
async def test_section_questions_database_error(client, mock_login_token):
    """
    Test section questions endpoint when a database error occurs
    """
    with (
        patch("ai_mf_backend.models.v1.database.questions.Section.objects.filter", side_effect=DatabaseError) as mock_section_filter,
        patch("ai_mf_backend.utils.v1.authentication.secrets.login_checker", return_value=True)
    ):
        # Act
        request_data = {"section_id": 1}
        response = client.post(SECTION_QUESTIONS_URL, 
                               json=request_data, 
                               headers=mock_login_token)

        # Assert
        assert response.status_code == 500
        response_data = response.json()
        
        assert response_data["status"] is False
        assert response_data["message"] == "A database error occurred."