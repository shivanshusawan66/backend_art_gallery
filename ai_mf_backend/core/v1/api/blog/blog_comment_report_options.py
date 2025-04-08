import logging
from fastapi import APIRouter
from ai_mf_backend.models.v1.api.blog_data import BlogCategoryOptionResponse
from ai_mf_backend.models.v1.database.blog import BlogCommentReportType

from asgiref.sync import sync_to_async

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/options_comment_report_type", response_model=BlogCategoryOptionResponse)
async def get_comment_report_type_options():
    try:
        report_types = await sync_to_async(list)(BlogCommentReportType.objects.all())
        type_options = [
            {
                "key": int(report_type.id),
                "label": report_type.report_type,
                "value": report_type.report_type.lower(),
            }
            for report_type in report_types
        ]

        data = {
            "report_types": {
                "name": "comment_report_type",
                "label": "Comment Report Type",
                "options": type_options,
                "type": "dropdown",
                "default": [type_options[0]["key"]] if type_options else [],
                "required": False,
            }
        }

        return BlogCategoryOptionResponse(
            status=True,
            message="Comment report type options fetched successfully",
            data=data,
            status_code=200,
        )

    except Exception as e:
        logger.error(f"Failed to fetch comment report type options: {e}")
        return BlogCategoryOptionResponse(
            status=False,
            message=f"Failed to fetch comment report type options: {str(e)}",
            data={},
            status_code=500,
        )
