import logging

from asgiref.sync import sync_to_async

from ai_mf_backend.models.v1.database.mf_embedding_tables import (
    MFMarkerOptions,
    MFMarker,
    Section,
)
from ai_mf_backend.utils.v1.errors import AssignWeightException

logger = logging.getLogger(__name__)


async def assign_initial_section_and_marker_weights():
    try:
        sections = await sync_to_async(list)(Section.objects.all())

        for section in sections:

            markers = await sync_to_async(list)(
                MFMarker.objects.filter(section_id=section)
            )
            total_markers = len(markers)

            if not total_markers:
                logger.warning(f"No markers found in Section ID {section.id}")
                raise AssignWeightException(
                    f"No markers found in Section {section.id}"
                )

            weight_per_marker = 1 / total_markers

            for marker in markers:
                marker.initial_marker_weight = weight_per_marker

                await sync_to_async(marker.save)()

                options = await sync_to_async(list)(
                    MFMarkerOptions.objects.filter(marker_id=marker)
                )
                total_responses = len(options)

                if not total_responses:
                    logger.warning(f"No responses found for Question ID {marker.id}")
                    raise AssignWeightException(
                        f"No responses found for Question {marker.id}"
                    )

                position = 1
                option_weight = 1 / total_responses

                for option in options:
                    option.position = position
                    option.option_weight = option_weight
                    position += 1

                    await sync_to_async(option.save)()

    except Exception as e:
        logger.error(f"Error assigning weight to sections and questions: {e}")
        raise AssignWeightException(
            f"Error assigning weight to sections and questions: {e}"
        )
