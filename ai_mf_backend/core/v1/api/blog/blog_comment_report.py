import logging
from fastapi import APIRouter,Depends,HTTPException,Response,status,Header
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.api.blog_comment_report import (ReportCreateRequest,ReportResponse)
from ai_mf_backend.utils.v1.authentication.secrets import login_checker,jwt_token_checker
from ai_mf_backend.models.v1.database.user import (UserContactInfo,UserPersonalDetails)
from ai_mf_backend.models.v1.database.blog import (BlogComment,BlogCommentReport,BlogCommentReportType,BlogCommentReply)


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
        
        user = await sync_to_async(UserContactInfo.objects.filter(email=email).first)()
        if not user:
            response.status_code = 400
            return ReportResponse(
                status=False,
                message="User not found",
                data=[],
                status_code=response.status_code
            )
        
        comment = None
        reply = None
        
        if request.comment_id:
            comment = await sync_to_async(BlogComment.objects.filter(id=request.comment_id).first)()
            if not comment:
                response.status_code = 404
                return ReportResponse(
                    status=False,
                    message="Comment not found",
                    data=[],
                    status_code=response.status_code
                )
        
        if request.reply_id:
            reply = await sync_to_async(BlogCommentReply.objects.filter(id=request.reply_id).first)()
            if not reply:
                response.status_code = 404
                return ReportResponse(
                    status=False,
                    message="Reply not found",
                    data=[],
                    status_code=response.status_code
                )
        
        report = await sync_to_async(BlogCommentReport.objects.create)(
            user=user,
            comment=comment,
            reply=reply,
            report_type=request.report_type
        )
        
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
