import logging
from fastapi import APIRouter,Depends,Response,Header
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.api.blog_comment_report import (ReportCreateRequest,ReportResponse)
from ai_mf_backend.utils.v1.authentication.secrets import login_checker,jwt_token_checker
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.database.blog import (
    BlogComment,
    BlogCommentReport,
    BlogCommentReportType,
    BlogCommentReply
)


router=APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/report",
    response_model=ReportResponse,
    dependencies=[Depends(login_checker)],
    status_code=200,
)
async def report_comment_or_reply(
    request: ReportCreateRequest,
    response: Response,
    Authorization: str = Header(),
):
    if not Authorization:
        response.status_code = 422
        return ReportResponse(
            status=False,
            message="Authorization header is missing.",
            data=[],
            status_code=422,
        )

    try:
        decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
        email = decoded_payload.get("email")
        mobile_no = decoded_payload.get("mobile_number")

        if not any([email, mobile_no]):
            response.status_code = 422
            return ReportResponse(
                status=False,
                message="Invalid JWT token: No email or mobile number found.", 
                data=[],
                status_code=response.status_code
            )


        user = await sync_to_async(lambda: UserContactInfo.objects.filter(email=email).first())()
        if not user:
            response.status_code = 400
            return ReportResponse(
                status=False,
                message="User not found",
                data=[],
                status_code=response.status_code
            )

        
        valid_ids = await sync_to_async(lambda: list(BlogCommentReportType.objects.values_list("id", flat=True)))()
        if request.report_type_id not in valid_ids:
            response.status_code = 400
            return ReportResponse(
                status=False,
                message=f"Invalid report type ID: {request.report_type_id}. Allowed IDs: {valid_ids}",
                data=[],
                status_code=response.status_code
            )

        
        try:
            report_type = await sync_to_async(lambda: BlogCommentReportType.objects.get(id=request.report_type_id))()
        except BlogCommentReportType.DoesNotExist:
            response.status_code = 400
            return ReportResponse(
                status=False,
                message="Invalid report type ID",
                data=[],
                status_code=response.status_code
            )

        comment, reply = None, None

        # Fetch comment if provided
        
        if request.comment_id and request.reply_id :
            response.status_code=400
            return ReportResponse(
                status=False,
                message="Only one is valid either comment or reply",
                data=[],
                status_code=response.status_code
            )
        if request.comment_id:
            comment = await sync_to_async(lambda: BlogComment.objects.filter(id=request.comment_id).first())()
            if not comment:
                response.status_code = 404
                return ReportResponse(
                    status=False,
                    message="Comment not found",
                    data=[],
                    status_code=response.status_code
                )

        # Fetch reply if provided
        if request.reply_id:
            reply = await sync_to_async(lambda: BlogCommentReply.objects.filter(id=request.reply_id).first())()
            if not reply:
                response.status_code = 404
                return ReportResponse(
                    status=False,
                    message="Reply not found",
                    data=[],
                    status_code=response.status_code
                )

        # Ensure at least one of comment/reply is provided
        if not comment and not reply:
            response.status_code = 400
            return ReportResponse(
                status=False,
                message="Either a comment or a reply must be provided.",
                data=[],
                status_code=response.status_code
            )


        report = await sync_to_async(lambda: BlogCommentReport.objects.create(
            user=user,
            comment=comment,
            reply=reply,
            report_type=report_type  
        ))()

        response.status_code = 201
        return ReportResponse(
            status=True,
            message="Report submitted successfully",
            data=[],
            status_code=response.status_code
        )

    except Exception as e:
        logger.error(f"Unexpected Error While Reporting: {e}")
        response.status_code = 500
        return ReportResponse(
            status=False,
            message="An unexpected error occurred",
            data=[],
            status_code=response.status_code
        )