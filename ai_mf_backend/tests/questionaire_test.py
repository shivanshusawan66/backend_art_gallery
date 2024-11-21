import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from asgiref.sync import sync_to_async

# Assuming the application is imported similarly
from ai_mf_backend.api_application import application


# Create a fixture for the test client
@pytest.fixture
def client():
    return TestClient(application)


# Tests for GET /sections endpoint
@pytest.mark.asyncio
@patch("ai_mf_backend.models.v1.database.questions.Section.objects")
async def test_get_all_sections_success(mock_sections, client):
    # Arrange
    mock_section1 = MagicMock()
    mock_section1.pk = 1
    mock_section1.section = "General Information"

    mock_section2 = MagicMock()
    mock_section2.pk = 2
    mock_section2.section = "Medical History"

    mock_sections.all = AsyncMock(return_value=[mock_section1, mock_section2])

    expected_response = {
        "status": True,
        "message": "Sections fetched successfully.",
        "data": [
            {"section_id": 1, "section_name": "General Information"},
            {"section_id": 2, "section_name": "Medical History"},
        ],
        "status_code": 200,
    }

    # Act
    response = client.get("/api/v1/sections")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.asyncio
@patch("ai_mf_backend.models.v1.database.questions.Section.objects")
async def test_get_all_sections_database_error(mock_sections, client):
    # Arrange
    mock_sections.all = AsyncMock(side_effect=Exception("Database connection error"))

    # Act
    response = client.get("/api/v1/sections")

    # Assert
    assert response.status_code == 500
    assert response.json() == {
        "status": False,
        "message": "Failed to fetch sections.",
        "data": None,
        "status_code": 500,
    }


# Tests for POST /section-wise-questions endpoint
@pytest.mark.asyncio
@patch("ai_mf_backend.models.v1.database.questions.Section.objects")
@patch("ai_mf_backend.models.v1.database.questions.Question.objects")
@patch("ai_mf_backend.models.v1.database.questions.Allowed_Response.objects")
@patch("ai_mf_backend.models.v1.database.questions.ConditionalQuestion.objects")
async def test_get_section_wise_questions_success(
    mock_conditional_questions,
    mock_allowed_responses,
    mock_questions,
    mock_sections,
    client,
):
    # Arrange
    section_id = 1
    mock_section = MagicMock()
    mock_section.pk = section_id
    mock_section.section = "General Information"
    mock_sections.filter.return_value.first = AsyncMock(return_value=mock_section)

    mock_question = MagicMock()
    mock_question.pk = 1
    mock_question.question = "What is your age?"
    mock_questions.filter.return_value = [mock_question]

    mock_options = [{"id": 1, "response": "18-25"}, {"id": 2, "response": "26-35"}]
    mock_allowed_responses.filter.return_value.values.return_value = mock_options

    # No conditional questions
    mock_conditional_questions.filter.return_value.values.return_value = []

    expected_response = {
        "status": True,
        "message": "Successfully fetched section wise questions and responses",
        "data": {
            "section_id": section_id,
            "section_name": "General Information",
            "questions": [
                {
                    "question_id": 1,
                    "question": "What is your age?",
                    "options": [
                        {"option_id": 1, "response": "18-25"},
                        {"option_id": 2, "response": "26-35"},
                    ],
                    "visibility_decisions": {"if_": []},
                }
            ],
        },
        "status_code": 200,
    }

    # Act
    response = client.post(
        "/api/v1/section-wise-questions/", json={"section_id": section_id}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.asyncio
@patch("ai_mf_backend.models.v1.database.questions.Section.objects")
async def test_get_section_wise_questions_section_not_found(mock_sections, client):
    # Arrange
    section_id = 999
    mock_sections.filter.return_value.first = AsyncMock(return_value=None)

    # Act
    response = client.post(
        "/api/v1/section-wise-questions/", json={"section_id": section_id}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "status": False,
        "message": "Section not found.",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_get_section_wise_questions_invalid_section_id(client):
    """Test case for invalid section ID format"""
    # Act
    response = client.post(
        "/api/v1/section-wise-questions/",
        json={"section_id": "invalid"},  # String instead of integer
    )

    # Assert
    assert response.status_code == 422
    assert response.json()["status_code"] == 422


@pytest.mark.asyncio
@patch("ai_mf_backend.models.v1.database.questions.Section.objects")
async def test_get_section_wise_questions_with_conditional_logic(mock_sections, client):
    """Test case for questions with conditional logic"""
    # Arrange
    section_id = 1
    mock_section = MagicMock()
    mock_section.pk = section_id
    mock_section.section = "Medical History"
    mock_sections.filter.return_value.first = AsyncMock(return_value=mock_section)

    mock_question = MagicMock()
    mock_question.pk = 1
    mock_question.question = "Do you have any allergies?"

    # Mock objects using AsyncMock for async operations
    with patch(
        "ai_mf_backend.models.v1.database.questions.Question.objects"
    ) as mock_questions, patch(
        "ai_mf_backend.models.v1.database.questions.Allowed_Response.objects"
    ) as mock_allowed_responses, patch(
        "ai_mf_backend.models.v1.database.questions.ConditionalQuestion.objects"
    ) as mock_conditional_questions:

        mock_questions.filter.return_value = [mock_question]

        mock_options = [{"id": 1, "response": "Yes"}, {"id": 2, "response": "No"}]
        mock_allowed_responses.filter.return_value.values.return_value = mock_options

        # Mock conditional question
        mock_conditional_info = {
            "dependent_question_id": 2,
            "response_id": 1,  # Response "Yes"
            "visibility": "show",
        }
        mock_conditional_questions.filter.return_value.values.return_value = [
            mock_conditional_info
        ]

        mock_condition_response = MagicMock()
        mock_condition_response.response = "Yes"
        mock_allowed_responses.filter.return_value.first.return_value = (
            mock_condition_response
        )

        # Act
        response = client.post(
            "/api/v1/section-wise-questions/", json={"section_id": section_id}
        )

    # Assert
    assert response.status_code == 200
    assert response.json()["data"]["questions"][0]["visibility_decisions"] == {
        "if_": [{"value": ["Yes"], "show": [2], "hide": []}]
    }


@pytest.mark.asyncio
@patch("ai_mf_backend.models.v1.database.questions.Section.objects")
async def test_get_section_wise_questions_database_error(mock_sections, client):
    # Arrange
    section_id = 1
    mock_sections.filter.return_value.first = AsyncMock(
        side_effect=Exception("Database error")
    )

    # Act
    response = client.post(
        "/api/v1/section-wise-questions/", json={"section_id": section_id}
    )

    # Assert
    assert response.status_code == 500
    assert response.json()["status_code"] == 500
