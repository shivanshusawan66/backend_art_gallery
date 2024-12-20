import logging

from celery import chain

from asgiref.sync import sync_to_async

from django.db import transaction

from ai_mf_backend.core.celery_init import celery_app

from ai_mf_backend.models.v1.database.questions import (
    Question,
    Allowed_Response,
    Section,
    UserResponse,
    QuestionWeightsPerUser,
    SectionWeightsPerUser,
)
from ai_mf_backend.utils.v1.errors import AssignWeightException

logger = logging.getLogger(__name__)


async def assign_initial_section_and_question_weights():
    try:
        with transaction.atomic():
            # Fetch all sections
            sections = await sync_to_async(list)(Section.objects.all)()
            total_sections = await sync_to_async(sections.count)()

            if not total_sections:
                logger.warning("No sections to assign weight")
                raise AssignWeightException("No sections found to assign weight")

            weight_per_section = 1 / total_sections

            # Process each section
            for section in sections:
                section.initial_section_weight = weight_per_section
                questions = await sync_to_async(Question.objects.filter)(
                    section=section
                )
                total_questions = await sync_to_async(questions.count)()

                if not total_questions:
                    logger.warning(
                        f"No questions found in Section ID {section.section}"
                    )
                    raise AssignWeightException(
                        f"No questions found in Section {section.section}"
                    )

                weight_per_question = 1 / total_questions

                for question in questions:
                    question.initial_question_weight = weight_per_question
                    responses = await sync_to_async(Allowed_Response.objects.filter)(
                        question=question
                    )
                    total_responses = await sync_to_async(responses.count)()

                    if not total_responses:
                        logger.warning(
                            f"No responses found for Question ID {question.question}"
                        )
                        raise AssignWeightException(
                            f"No responses found for Question {question.question}"
                        )
                    position = 1
                    response_weight = total_responses / 5
                    for response in responses:
                        response.position = position
                        response.response_weight = response_weight
                        position += 1
                        await sync_to_async(response.save)()
                    await sync_to_async(question.save)()
                await sync_to_async(section.save)()
    except Exception as e:
        logger.error(f"Error assigning weight to sections and questions: {e}")
        raise AssignWeightException(
            f"Error assigning weight to sections and questions: {e}"
        )


@celery_app.task(acks_late=False, ignore_result=True, bind=True)
async def assign_final_question_weights(self, user_id: int):

    try:
        with transaction.atomic():
            # Fetch all sections
            user_responses = await sync_to_async(UserResponse.objects.filter)(
                user_id=user_id
            )
            for response in user_responses:

                allowed_response = await sync_to_async(
                    Allowed_Response.objects.filter(pk=response.response_id).first
                )()
                response_score = (
                    allowed_response.response_weight * allowed_response.position
                )

                question = await sync_to_async(
                    Question.objects.filter(question=response.question_id).first
                )()
                question_weight_for_user = QuestionWeightsPerUser(
                    user_id=user_id,
                    question=response.question_id,
                    section=response.section_id,
                    weight=response_score * question.initial_question_weight,
                )
                await sync_to_async(question_weight_for_user.save)()
                return user_id
    except Exception as e:
        logger.error(f"Error assigning final question weights for user {user_id}: {e}")
        raise AssignWeightException(
            f"Error assigning final question weights for user {user_id}: {e}"
        )


@celery_app.task(acks_late=False, ignore_result=True, bind=True)
async def assign_final_section_weights(self, user_id: int):
    try:
        with transaction.atomic():
            questions = await sync_to_async(list)(
                QuestionWeightsPerUser.objects.filter(user_id=user_id)
            )
            sections = await sync_to_async(list)(Section.objects.all())
            for section in sections:
                final_section_weight = 0
                for question in questions:
                    if question.section == section.pk:
                        final_section_weight += question.weight
                    else:
                        continue
                section_weight_for_user = SectionWeightsPerUser(
                    user_id=user_id,
                    section=section.pk,
                    weight=final_section_weight * section.initial_section_weight,
                )
                await sync_to_async(section_weight_for_user.save)()
    except Exception as e:
        logger.error(f"Error assigning final section weights for user {user_id}: {e}")
        raise AssignWeightException(
            f"Error assigning final section weights for user {user_id}: {e}"
        )


async def assign_user_weights_chain(user_id: int):
    try:
        task_chain = chain(
            assign_final_question_weights.s(user_id), assign_final_section_weights.s()
        )
        task_chain.apply_async()
    except Exception as e:
        logger.error(f"Error assigning weights for user {user_id}: {e}")
        raise AssignWeightException(f"Error assigning weights for user {user_id}: {e}")
