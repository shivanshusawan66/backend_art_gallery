import logging
from fastapi import APIRouter, Depends, HTTPException,Response,status,Header
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.database.blog import BlogComment
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.database.user import UserPersonalDetails
from ai_mf_backend.models.v1.database.blog import BlogCommentReply
from ai_mf_backend.models.v1.api.blog_comment_reply import ( CommentReplyData,CommentReplyResponse,CommentReplyCreateRequest)


from ai_mf_backend.utils.v1.authentication.secrets import login_checker,jwt_token_checker
router=APIRouter()
logger=logging.getLogger(__name__)

@router.post("/comment_reply",response_model=CommentReplyResponse, dependencies=[Depends(login_checker)],
    status_code=200,)
async def post_comment_reply(request:CommentReplyCreateRequest,
 response: Response, 
 Authorization: str = Header(),
):  
    if not Authorization:
        response.status_code = 422
        return CommentReplyResponse(
            status=False,
            message="Authorization header is missing.",
            data=[],
            status_code=422,
        )
    try:
        decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
        email = decoded_payload.get("email")
        mobile_no = decoded_payload.get("mobile_number")

        
        if request.comment_id is None:
            response_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return CommentReplyResponse(
                status=False,
                message="comment id is required",
                data=[],
                status_code=response_status_code,
            )
        
        
        if not any([email, mobile_no]):
            response.status_code = 422
            return CommentReplyResponse(
                status=False,
                message="Invalid JWT token: no email or mobile number found.",
                data=[],
                status_code=response.status_code,
            )

        user = None
        if email:
            user = await UserContactInfo.objects.filter(email=email).afirst()
        elif mobile_no:
            user = await UserContactInfo.objects.filter(mobile_number=mobile_no).afirst()

        
        if not user:
            response.status_code = 400
            return CommentReplyResponse(
                status=False,
                message="User not found",
                data=[],
                status_code=response.status_code,
            )
        
        new_comment_reply = await sync_to_async(BlogCommentReply.objects.create)(
            parent_comment_id=request.comment_id, 
            user=user,
            content=request.content
        )

        
        response.status_code = 201
        return CommentReplyResponse(
            status=True,
            message="Reply added successfully to the comment",
            data=[],
            status_code=response.status_code,
        )

    except Exception as e:
        logger.error(f"Unexpected Error While Posting Comments: {e}")
        response.status_code = 500

        return CommentReplyResponse(
            status=False,
            message="An unexpected error occurred",
            data=[],  
            status_code=response.status_code,
        )
    


@router.get("/comment_reply/{comment_id}", response_model=CommentReplyResponse)
async def get_comment_replies( comment_id: int, response: Response):
    try:
        replies = await sync_to_async(list)(
            BlogCommentReply.objects.filter(parent_comment_id=comment_id, deleted=False)
            .select_related("user")
            .order_by("created_at")
        )

        formatted_replies = []

        for reply in replies:
            username = "Anonymous"  
            if reply.user:
                user_details = await sync_to_async(UserPersonalDetails.objects.filter(user=reply.user).first)()
                if user_details and user_details.name:
                    username = user_details.name

            formatted_replies.append(
                CommentReplyData(
                    id=reply.id,
                    user=username,
                    content=reply.content,
                    created_at=reply.created_at
                )
            )

        return CommentReplyResponse(
            status=True,
            message="Replies retrieved successfully",
            data=formatted_replies,
            status_code=200
        )

    except Exception as e:
        response.status_code = 500
        return CommentReplyResponse(
            status=False,
            message=f"Error: {str(e)}",
            data=[],
            status_code=response.status_code
        )
