import logging

from celery import chain

from asgiref.sync import sync_to_async

from django.db import transaction

from ai_mf_backend.core import celery_app

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


@celery_app.task(acks_late=False, bind=True)
async def assign_final_question_weights(self, user_id: int):
    logger.info("the assign final question weight started step-0")
    try:
        with transaction.atomic():
            # Fetch all sections
            logger.info("the assign final question weight started step-1")
            user_responses = await sync_to_async(UserResponse.objects.filter)(
                user_id_id=user_id
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
                    user_id_id=user_id,
                    question=response.question_id,
                    section=response.section_id,
                    weight=response_score * question.initial_question_weight,
                )
                logger.info(f"question weight saved {user_id}")
                await sync_to_async(question_weight_for_user.save)()
    except Exception as e:
        logger.error(f"Error assigning final question weights for user {user_id}: {e}")
        raise AssignWeightException(
            f"Error assigning final question weights for user {user_id}: {e}"
        )


@celery_app.task(acks_late=False, bind=True)
async def assign_final_section_weights(self, user_id: int):
    try:
        with transaction.atomic():
            questions = await sync_to_async(list)(
                QuestionWeightsPerUser.objects.filter(user_id_id=user_id)
            )
            sections = await sync_to_async(list)(Section.objects.all())
            for section in sections:
                final_section_weight = 0
                for question in questions:
                    if question.section == section.id:
                        final_section_weight += question.weight
                    else:
                        continue
                section_weight_for_user = SectionWeightsPerUser(
                    user_id_id=user_id,
                    section=section.pk,
                    weight=final_section_weight * section.initial_section_weight,
                )
                logger.info(f"question weight saved {user_id}")
                await sync_to_async(section_weight_for_user.save)()
    except Exception as e:
        logger.error(f"Error assigning final section weights for user {user_id}: {e}")
        raise AssignWeightException(
            f"Error assigning final section weights for user {user_id}: {e}"
        )


async def assign_user_weights_chain(user_id: int):
    try:
        task_chain = chain(
            assign_final_question_weights.si(user_id), assign_final_section_weights.si(user_id)
        )
        logger.info(f"chain called {user_id}")
        task_chain.apply_async()
        logger.info(f"chain called done {user_id}")
    except Exception as e:
        logger.error(f"Error assigning weights for user {user_id}: {e}")
        raise AssignWeightException(f"Error assigning weights for user {user_id}: {e}")
