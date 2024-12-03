import logging
from typing import List, Optional
from django.db import transaction
from celery import chain
from celery.result import AsyncResult
from ai_mf_backend.core import celery_app
from ai_mf_backend.models.v1.database.questions import (
    Question,
    Allowed_Response,
    Section,
)
from ai_mf_backend.utils.v1.errors import AssignWeightException

logger = logging.getLogger(__name__)

def assign_section_and_question_weights():
    """
    Assign equal weights to sections and their respective questions.
    
    Raises:
        AssignWeightException: If no sections or questions are found
    """
    try:
        with transaction.atomic():
            # Fetch all sections
            sections = Section.objects.all()
            num_sections = sections.count()

            if num_sections == 0:
                logger.warning("No sections to assign weight")
                raise AssignWeightException("No sections found to assign weight")

            weight_per_section = 1 / num_sections

            # Process each section
            for section in sections:
                section.section_weight = weight_per_section
                questions = Question.objects.filter(section=section)
                total_questions = questions.count()

                if total_questions == 0:
                    logger.warning(f"No questions found in Section ID {section.section}")
                    raise AssignWeightException(f"No questions found in Section {section.section}")
                
                weight_per_question = 1 / total_questions

                for question in questions:
                    question.question_weight = weight_per_question
                    responses=Allowed_Response.objects.filter(question=question)
                    total_responses = responses.count()

                    if total_responses == 0:
                        logger.warning(f"No responses found for Question ID {question.question}")
                        raise AssignWeightException(f"No responses found for Question {question.question}")
                    
                    weight_per_response = 0
                    for response in responses:
                        
                    

                    question.save()

                section.save()
    except Exception as e:
        logger.error(f"Error assigning weight to sections and questions: {e}")
        raise AssignWeightException(f"Error assigning weight to sections and questions: {e}")
    
        

# @celery_app.task(acks_late=True, ignore_result=False, bind=True)
# def calculate_option_scores(self, question_id: int) -> dict:
#     """
#     Calculate weight_per_option and option_score for each allowed response.
    
#     Args:
#         question_id (int): ID of the question to process
    
#     Returns:
#         dict: Calculation results or error information
#     """
#     try:
#         with transaction.atomic():
#             question = Question.objects.select_for_update().get(id=question_id)
#             responses = Allowed_Response.objects.filter(question=question)
#             num_options = responses.count()

#             if num_options == 0 or question.base_weight <= 0:
#                 logger.warning(f"Invalid base_weight or no responses for Question ID {question_id}")
#                 return {
#                     "status": "warning",
#                     "message": "No valid options or base weight",
#                     "question_id": question_id
#                 }

#             weight_per_option = question.base_weight / num_options

#             for response in responses:
#                 response.weight_per_option = weight_per_option
#                 response.option_score = weight_per_option * (response.position or 0)
#                 response.save()

#             return {
#                 "status": "success",
#                 "question_id": question_id,
#                 "weight_per_option": weight_per_option,
#                 "num_options": num_options
#             }

#     except Question.DoesNotExist:
#         logger.error(f"Question with ID {question_id} not found")
#         return {
#             "status": "error",
#             "message": f"Question {question_id} does not exist",
#             "question_id": question_id
#         }
#     except Exception as e:
#         logger.exception(f"Error in calculate_option_scores for Question ID {question_id}")
#         return {
#             "status": "error",
#             "message": str(e),
#             "question_id": question_id
#         }


# @celery_app.task(acks_late=True, ignore_result=False, bind=True)
# def calculate_question_score(self, question_id: int) -> dict:
#     """
#     Calculate the aggregated score for a question.
    
#     Args:
#         question_id (int): ID of the question to process
    
#     Returns:
#         dict: Calculation results or error information
#     """
#     try:
#         with transaction.atomic():
#             question = Question.objects.select_for_update().get(id=question_id)
#             responses = Allowed_Response.objects.filter(question=question)

#             total_option_scores = sum(response.option_score for response in responses)
#             num_options = responses.count()

#             question.question_score = (
#                 question.initial_weight * total_option_scores 
#                 if num_options > 0 
#                 else 0.0
#             )
#             question.save()

#             return {
#                 "status": "success",
#                 "question_id": question_id,
#                 "question_score": question.question_score,
#                 "num_options": num_options
#             }

#     except Question.DoesNotExist:
#         logger.error(f"Question with ID {question_id} not found")
#         return {
#             "status": "error",
#             "message": f"Question {question_id} does not exist",
#             "question_id": question_id
#         }
#     except Exception as e:
#         logger.exception(f"Error in calculate_question_score for Question ID {question_id}")
#         return {
#             "status": "error",
#             "message": str(e),
#             "question_id": question_id
#         }


# @celery_app.task(acks_late=True, ignore_result=False, bind=True)
# def calculate_section_score(self, section_id: int) -> dict:
#     """
#     Calculate the aggregated score for a section.
    
#     Args:
#         section_id (int): ID of the section to process
    
#     Returns:
#         dict: Calculation results or error information
#     """
#     try:
#         with transaction.atomic():
#             section = Section.objects.select_for_update().get(id=section_id)
#             questions = Question.objects.filter(section=section)

#             total_question_scores = sum(question.question_score for question in questions)
#             num_questions = questions.count()

#             section.section_score = (
#                 total_question_scores / num_questions 
#                 if num_questions > 0 
#                 else 0.0
#             )
#             section.save()

#             return {
#                 "status": "success",
#                 "section_id": section_id,
#                 "section_score": section.section_score,
#                 "num_questions": num_questions
#             }

#     except Section.DoesNotExist:
#         logger.error(f"Section with ID {section_id} not found")
#         return {
#             "status": "error",
#             "message": f"Section {section_id} does not exist",
#             "section_id": section_id
#         }
#     except Exception as e:
#         logger.exception(f"Error in calculate_section_score for Section ID {section_id}")
#         return {
#             "status": "error",
#             "message": str(e),
#             "section_id": section_id
#         }


# def create_score_recalculation_chain(section: Section) -> Optional[AsyncResult]:
#     """
#     Create a Celery task chain for recalculating scores for a specific section.
    
#     Args:
#         section (Section): Section to recalculate scores for
    
#     Returns:
#         Optional[AsyncResult]: Celery async result for the task chain, or None if no questions
#     """
#     # Fetch all questions for the section with related data in a single query
#     questions = Question.objects.filter(section=section)

#     if not questions:
#             logger.warning(f"No questions found for Section ID {section.id}")
#             return None

#     question_tasks = [
#         chain(
#             calculate_option_scores.s(question.id),
#             calculate_question_score.s(question.id),
#         )
#         for question in questions
#     ]
    
    
#     # If no tasks were created, return None
#     if not question_tasks:
#         logger.warning(f"No tasks created for Section ID {section.id}")
#         return None

#     # Create final task chain including section score calculation
#     section_task = chain(*question_tasks, calculate_section_score.s(section.id))
    
#     # Apply the task chain asynchronously
#     return section_task.apply_async()

@celery_app.task(acks_late=True, ignore_result=True, bind=True)
def recalculate_scores_on_update(
    self, 
    section_ids: Optional[List[int]] = None
) -> None:
    """
    Recalculate all scores when there are updates.
    
    Args:
        section_ids (Optional[List[int]], optional): List of section IDs to recalculate. 
                                                     If None, recalculate all sections.
    """
    try:
        # If no section_ids are provided, recalculate for all sections
        if section_ids is None:
            sections = Section.objects.all()
        else:
            # Recalculate for the specified sections only
            sections = Section.objects.filter(id__in=section_ids)

        if not sections:
            logger.warning(
                "No sections found for the provided section IDs or all sections."
            )
            return

        for section in sections:
            create_score_recalculation_chain(section)
            logger.info(f"Triggered recalculation for Section ID {section.id}")

    except Exception as e:
        logger.exception("Error in recalculate_scores_on_update")
        raise