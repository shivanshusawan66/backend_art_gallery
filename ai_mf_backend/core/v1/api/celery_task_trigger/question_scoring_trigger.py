import logging
from fastapi import APIRouter, HTTPException, Depends, Response, Header
from ai_mf_backend.utils.v1.authentication.secrets import login_checker
from ai_mf_backend.models.v1.api.task_trigger import (
    TaskTriggerResponse,
    TriggerTaskRequest,
)
from ai_mf_backend.celery_tasks import recalculate_scores_on_update

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/trigger-tasks/",
    response_model=TaskTriggerResponse,
    dependencies=[Depends(login_checker)],
)
async def trigger_celery_tasks(
    request: TriggerTaskRequest,
    response: Response,
    Authorization: str = Header(),
):
    try:
        # Check if section IDs are provided
        if request and request.section_ids:
            # Recalculate only for the provided sections
            recalculate_scores_on_update.apply_async(args=[request.section_ids])
            message = f"Tasks triggered for sections {request.section_ids}."
        else:
            # Recalculate for all sections
            recalculate_scores_on_update.apply_async(args=[None])
            message = "Tasks triggered for all sections."

        return TaskTriggerResponse(success=True, message=message)

    except Exception as e:
        logger.error(f"Error triggering tasks: {e}")
        response.status_code = 500
        return TaskTriggerResponse(
            success=False, message=f"Error triggering tasks: {str(e)}"
        )
