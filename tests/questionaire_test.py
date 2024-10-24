import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from ai_mf_backend.api_application import application

# Create a fixture for the test client
@pytest.fixture
def client():
    return TestClient(application)

# Tests for GET /sections endpoint
@patch('ai_mf_backend.models.v1.database.questions.Section.objects')
def test_get_all_sections_success(mock_sections, client):
    # Arrange
    mock_section1 = MagicMock()
    mock_section1.pk = 1
    mock_section1.section_name = "General Information"
    
    mock_section2 = MagicMock()
    mock_section2.pk = 2
    mock_section2.section_name = "Medical History"
    
    mock_sections.all.return_value = [mock_section1, mock_section2]
    
    expected_response = {
        "data": [
            {"section_id": 1, "section_name": "General Information"},
            {"section_id": 2, "section_name": "Medical History"}
        ]
    }
    
    # Act
    response = client.get("/api/v1/sections")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == expected_response
    mock_sections.all.assert_called_once()

@patch('ai_mf_backend.models.v1.database.questions.Section.objects')
def test_get_all_sections_empty(mock_sections, client):
    # Arrange
    mock_sections.all.return_value = []
    expected_response = {"data": []}
    
    # Act
    response = client.get("/api/v1/sections")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == expected_response
    mock_sections.all.assert_called_once()

@patch('ai_mf_backend.models.v1.database.questions.Section.objects')
def test_get_all_sections_database_error(mock_sections, client):
    # Arrange
    mock_sections.all.side_effect = Exception("Database connection error")
    
    # Act
    response = client.get("/api/v1/sections")
    
    # Assert
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to fetch sections."}

# # Tests for POST /section-wise-questions endpoint
@pytest.mark.parametrize("section_id", [1])
@patch('ai_mf_backend.models.v1.database.questions.ConditionalQuestion.objects')
@patch('ai_mf_backend.models.v1.database.questions.Allowed_Response.objects')
@patch('ai_mf_backend.models.v1.database.questions.Question.objects')
@patch('ai_mf_backend.models.v1.database.questions.Section.objects')
def test_get_section_wise_questions_success(
    mock_sections, mock_questions, mock_allowed_responses,
    mock_conditional_questions, client, section_id
):
    # Arrange
    mock_section = MagicMock()
    mock_section.pk = section_id
    mock_section.section_name = "General Information"
    mock_sections.filter.return_value.first.return_value = mock_section
   
    mock_question = MagicMock()
    mock_question.pk = 1
    mock_question.question = "What is your age?"
    mock_questions.filter.return_value = [mock_question]
   
    mock_responses = [
        {"id": 1, "response": "18-25"},
        {"id": 2, "response": "26-35"}
    ]
    mock_allowed_responses.filter.return_value.values.return_value = mock_responses
   
    # Create a mock queryset with exists() method
    mock_queryset = MagicMock()
    mock_queryset.exists.return_value = False
    mock_conditional_questions.filter.return_value = mock_queryset
   
    expected_response = {
        "status_code": 200,  # Added status_code to match actual response
        "data": {
            "section_id": section_id,
            "section_name": "General Information",
            "questions": [{
                "question_id": 1,
                "question": "What is your age?",
                "options": [
                    {"option_id": 1, "response": "18-25"},
                    {"option_id": 2, "response": "26-35"}
                ],
                "visibility_decisions": {"if_": []}
            }]
        }
    }
   
    # Act
    response = client.post(
        "/api/v1/section-wise-questions/",
        json={"section_id": section_id}
    )
   
    # Assert
    assert response.status_code == 200
    assert response.json() == expected_response

@patch('ai_mf_backend.models.v1.database.questions.ConditionalQuestion.objects')
@patch('ai_mf_backend.models.v1.database.questions.Allowed_Response.objects')
@patch('ai_mf_backend.models.v1.database.questions.Question.objects')
@patch('ai_mf_backend.models.v1.database.questions.Section.objects')
def test_get_section_wise_questions_with_conditional_logic(
    mock_sections, mock_questions, mock_allowed_responses,
    mock_conditional_questions, client
):
    # Arrange
    section_id = 1
   
    mock_section = MagicMock()
    mock_section.pk = section_id
    mock_section.section_name = "Medical History"
    mock_sections.filter.return_value.first.return_value = mock_section
   
    mock_question = MagicMock()
    mock_question.pk = 1
    mock_question.question = "Do you have any allergies?"
    mock_questions.filter.return_value = [mock_question]
   
    mock_responses = [
        {"id": 1, "response": "Yes"},
        {"id": 2, "response": "No"}
    ]
    mock_allowed_responses.filter.return_value.values.return_value = mock_responses
   
    mock_dependent_question = MagicMock()
    mock_dependent_question.id = 2
   
    mock_conditional = MagicMock()
    mock_conditional.dependent_question = mock_dependent_question
    mock_conditional.visibility = "show"
    mock_conditional.condition_id = 1
   
    mock_condition_response = MagicMock()
    mock_condition_response.response = "Yes"
    mock_allowed_responses.filter.return_value.first.return_value = mock_condition_response
   
    # Create a mock queryset that has both exists() and iteration capability
    mock_queryset = MagicMock()
    mock_queryset.exists.return_value = True
    mock_queryset.__iter__.return_value = iter([mock_conditional])
    mock_conditional_questions.filter.return_value = mock_queryset
   
    expected_response = {
        "status_code": 200,
        "data": {
            "section_id": section_id,
            "section_name": "Medical History",
            "questions": [{
                "question_id": 1,
                "question": "Do you have any allergies?",
                "options": [
                    {"option_id": 1, "response": "Yes"},
                    {"option_id": 2, "response": "No"}
                ],
                "visibility_decisions": {
                    "if_": [{
                        "value": ["Yes"],
                        "show": [2]
                    }]
                }
            }]
        }
    }
   
    # Act
    response = client.post(
        "/api/v1/section-wise-questions/",
        json={"section_id": section_id}
    )
   
    # Assert
    assert response.status_code == 200
    assert response.json() == expected_response




@patch('ai_mf_backend.models.v1.database.questions.Section.objects')
def test_get_section_wise_questions_section_not_found(mock_sections, client):
    # Arrange
    section_id = 999
    mock_sections.filter.return_value.first.return_value = None
    
    # Act
    response = client.post(
        "/api/v1/section-wise-questions/",
        json={"section_id": section_id}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json() == {"status_code": 404,
                    "detail": "Section not found."}

@patch('ai_mf_backend.models.v1.database.questions.Section.objects')
def test_get_section_wise_questions_database_error(mock_sections, client):
    # Arrange
    section_id = 1
    mock_sections.filter.side_effect = Exception("Database error")
    
    # Act
    response = client.post(
        "/api/v1/section-wise-questions/",
        json={"section_id": section_id}
    )
    
    # Assert
    assert response.status_code == 500
    assert response.json() == {"status_code": 500,
                "detail": "Database error"}
    

