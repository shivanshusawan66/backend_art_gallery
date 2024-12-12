import logging
from django.db import transaction
from ai_mf_backend.models.v1.database.questions import (
    Question,
    Allowed_Response,
    Section,
    UserResponse
)
from ai_mf_backend.utils.v1.errors import AssignWeightException

logger = logging.getLogger(__name__)

def assign_initial_section_and_question_weights():
    """
    Assign equal weights to sections and their respective questions.
    
    Raises:
        AssignWeightException: If no sections or questions are found
    """
    try:
        with transaction.atomic():
            # Fetch all sections
            sections = Section.objects.all()
            total_sections = sections.count()

            if not total_sections:
                logger.warning("No sections to assign weight")
                raise AssignWeightException("No sections found to assign weight")

            weight_per_section = 1 / total_sections

            # Process each section
            for section in sections:
                section.initial_section_weight = weight_per_section
                questions = Question.objects.filter(section=section)
                total_questions = questions.count()

                if not total_questions:
                    logger.warning(f"No questions found in Section ID {section.section}")
                    raise AssignWeightException(f"No questions found in Section {section.section}")
                
                weight_per_question = 1 / total_questions

                for question in questions:
                    question.initial_question_weight = weight_per_question
                    responses=Allowed_Response.objects.filter(question=question)
                    total_responses = responses.count()

                    if not total_responses:
                        logger.warning(f"No responses found for Question ID {question.question}")
                        raise AssignWeightException(f"No responses found for Question {question.question}")
                    position=1
                    total_responses=responses.count()
                    response_weight=total_responses/5
                    for response in responses:
                        response.position=position
                        response.response_weight=response_weight
                        position+=1
                        response.save()
                    question.save()
                section.save()
    except Exception as e:
        logger.error(f"Error assigning weight to sections and questions: {e}")
        raise AssignWeightException(f"Error assigning weight to sections and questions: {e}")
    

def assign_final_question_weights(user_id : int):

    try:
        with transaction.atomic():
            # Fetch all sections
            user_responses=UserResponse.objects.filter(user_id=user_id)
            for response in user_responses:

                response=Allowed_Response.objects.filter(pk=response.response_id).first()
                response_score=response.response_weight * response.position

                question=Question.objects.filter(question=response.question_id).first()
                question.final_question_weight=response_score*question.initial_question_weight
                question.save()
    except Exception as e:
        logger.error(f"Error assigning final question weights for user {user_id}: {e}")
        raise AssignWeightException(f"Error assigning final question weights for user {user_id}: {e}")


def assign_final_section_weights(user_id : int):
    try:
        with transaction.atomic():
            questions = Question.objects.all()
            sections = Section.objects.all()
            for section in sections:
                final_section_weight=0
                for question in questions:
                    if question.section==section.pk:
                        final_section_weight+=question.final_question_weight
                    else:
                        continue
                section.final_section_weight=final_section_weight*section.initial_section_weight
    except Exception as e:
        logger.error(f"Error assigning final section weights for user {user_id}: {e}")
        raise AssignWeightException(f"Error assigning final section weights for user {user_id}: {e}")
    
    