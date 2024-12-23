import logging

from asgiref.sync import sync_to_async

from ai_mf_backend.models.v1.database.questions import (
    Allowed_Response,
    Question,
    Section,
)
from ai_mf_backend.utils.v1.errors import AssignWeightException

logger = logging.getLogger(__name__)


async def assign_initial_section_and_question_weights():
    try:
        # Fetch all sections
        sections = await sync_to_async(list)(Section.objects.all())
        total_sections = len(sections)

        if not total_sections:
            logger.warning("No sections to assign weight")
            raise AssignWeightException("No sections found to assign weight")

        weight_per_section = 1 / total_sections

        for section in sections:
            section.initial_section_weight = weight_per_section

            # Save section asynchronously
            await sync_to_async(section.save)()

            # Fetch all questions for this section
            questions = await sync_to_async(list)(
                Question.objects.filter(section=section)
            )
            total_questions = len(questions)

            if not total_questions:
                logger.warning(f"No questions found in Section ID {section.id}")
                raise AssignWeightException(
                    f"No questions found in Section {section.id}"
                )

            weight_per_question = 1 / total_questions

            for question in questions:
                question.initial_question_weight = weight_per_question

                # Save question asynchronously
                await sync_to_async(question.save)()

                # Fetch all responses for this question
                responses = await sync_to_async(list)(
                    Allowed_Response.objects.filter(question=question)
                )
                total_responses = len(responses)

                if not total_responses:
                    logger.warning(f"No responses found for Question ID {question.id}")
                    raise AssignWeightException(
                        f"No responses found for Question {question.id}"
                    )

                position = 1
                response_weight = 1 / total_responses  # Divide evenly across responses

                for response in responses:
                    response.position = position
                    response.response_weight = response_weight
                    position += 1

                    # Save response asynchronously
                    await sync_to_async(response.save)()

    except Exception as e:
        logger.error(f"Error assigning weight to sections and questions: {e}")
        raise AssignWeightException(
            f"Error assigning weight to sections and questions: {e}"
        )
