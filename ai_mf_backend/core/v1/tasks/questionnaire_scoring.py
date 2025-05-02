import logging

from celery import chain
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
def assign_final_question_weights(self, user_id: int):
    try:
        with transaction.atomic():
            # Fetch all sections
            user_responses = UserResponse.objects.filter(user_id_id=user_id)
            for response in user_responses:
                response_id = int(response.response_id.id)
                allowed_response = Allowed_Response.objects.filter(
                    pk=response_id
                ).first()
                response_score = (
                    allowed_response.response_weight * allowed_response.position
                )
                question = Question.objects.filter(
                    question=response.question_id
                ).first()
                question_weight_for_user = QuestionWeightsPerUser.objects.filter(
                    user_id_id=user_id,
                    question=response.question_id,
                    section=response.section_id,
                ).first()
                if question_weight_for_user:
                    question_weight_for_user.weight = (
                        response_score * question.initial_question_weight
                    )
                    question_weight_for_user.save()
                else:
                    question_weight_for_user = QuestionWeightsPerUser(
                        user_id_id=user_id,
                        question=response.question_id,
                        section=response.section_id,
                        weight=response_score * question.initial_question_weight,
                    )
                logger.info(f"question weight saved {user_id}")
                question_weight_for_user.save()
    except Exception as e:
        logger.error(f"Error assigning final question weights for user {user_id}: {e}")
        raise AssignWeightException(
            f"Error assigning final question weights for user {user_id}: {e}"
        )


@celery_app.task(acks_late=False, bind=True)
def assign_final_section_weights(self, user_id: int):
    try:
        with transaction.atomic():
            questions = QuestionWeightsPerUser.objects.filter(user_id_id=user_id)
            sections = Section.objects.all().order_by("id")
            embedding_array = []
            for section in sections:
                final_section_weight = 0
                for question in questions:
                    if question.section == section:
                        final_section_weight += question.weight
                    else:
                        continue
                if final_section_weight:
                    embedding_array.append(final_section_weight)
                else:
                    embedding_array.append(0.001)

            section_weight_for_user = SectionWeightsPerUser.objects.filter(
                user_id_id=user_id
            ).first()

            if section_weight_for_user:
                section_weight_for_user.embedding = embedding_array
                section_weight_for_user.save()
            else:
                section_weight_for_user = SectionWeightsPerUser(
                    user_id_id=user_id,
                    embedding=embedding_array,
                )
            logger.info(f"section weight saved {user_id}")
            section_weight_for_user.save()
    except Exception as e:
        logger.error(f"Error assigning final section weights for user {user_id}: {e}")
        raise AssignWeightException(
            f"Error assigning final section weights for user {user_id}: {e}"
        )


async def assign_user_weights_chain(user_id: int):
    try:
        task_chain = chain(
            assign_final_question_weights.si(user_id),
            assign_final_section_weights.si(user_id),
        )
        task_chain.apply_async()
    except Exception as e:
        logger.error(f"Error assigning weights for user {user_id}: {e}")
        raise AssignWeightException(f"Error assigning weights for user {user_id}: {e}")
