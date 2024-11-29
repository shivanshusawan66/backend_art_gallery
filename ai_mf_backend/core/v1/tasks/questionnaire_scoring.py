import logging
from celery import chain
from ai_mf_backend.core import celery_app
from ai_mf_backend.models.v1.database.questions import (
    Question,
    Allowed_Response,
    Section,
)

logger = logging.getLogger(__name__)


@celery_app.task(acks_late=False, ignore_result=True, bind=True)
def calculate_option_scores(self, question_id):
    """Calculate weight_per_option and option_score for each allowed response."""
    try:
        question = Question.objects.get(id=question_id)
        responses = Allowed_Response.objects.filter(question=question)
        num_options = responses.count()

        if num_options == 0 or question.base_weight <= 0:
            print(f"Invalid base_weight or no responses for Question ID {question_id}.")
            return

        weight_per_option = question.base_weight / num_options

        for response in responses:
            response.weight_per_option = weight_per_option
            response.option_score = weight_per_option * (response.position or 0)
            response.save()
    except Exception as e:
        print(f"Error in calculate_option_scores: {e}")


@celery_app.task(acks_late=False, ignore_result=True, bind=True)
def calculate_question_score(self, question_id):
    """Calculate the aggregated score for a question."""
    try:
        question = Question.objects.get(id=question_id)
        responses = Allowed_Response.objects.filter(question=question)

        total_option_scores = sum([response.option_score for response in responses])
        num_options = responses.count()

        if num_options > 0:
            question.question_score = question.initial_weight * total_option_scores
        else:
            question.question_score = 0.0

        question.save()
        logger.info(f"Updated question_score for Question ID {question_id}")
    except Exception as e:
        logger.error(f"Error in calculate_question_score: {e}")


@celery_app.task(acks_late=False, ignore_result=True, bind=True)
def calculate_section_score(self, section_id):
    """Calculate the aggregated score for a section."""
    section = Section.objects.get(id=section_id)
    questions = Question.objects.filter(section=section)

    total_question_scores = sum([question.question_score for question in questions])
    num_questions = questions.count()

    if num_questions > 0:
        section.section_score = total_question_scores / num_questions
    else:
        section.section_score = 0.0

    section.save()


@celery_app.task(acks_late=False, ignore_result=True, bind=True)
def recalculate_scores_on_update(self, section_ids=None):
    """Recalculate all scores when there are updates. Optionally for specific sections."""
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
            question_tasks = [
                chain(
                    calculate_option_scores.s(question.id),
                    calculate_question_score.s(question.id),
                )
                for question in Question.objects.filter(section=section)
            ]
            section_task = chain(*question_tasks, calculate_section_score.s(section.id))

            section_task.apply_async()
            logger.info(f"Triggered recalculation for Section ID {section.id}")

    except Exception as e:
        logger.error(f"Error in recalculate_scores_on_update: {e}")
        raise
