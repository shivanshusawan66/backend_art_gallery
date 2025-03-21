import logging
from fastapi import APIRouter, Depends, HTTPException,Response,status
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.database.blog import BlogComment
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.database.user import UserPersonalDetails

from ai_mf_backend.models.v1.api.blog_comment import (
    CommentResponse, CommentData, CommentCreateRequest, CommentUpdateRequest
)
from ai_mf_backend.utils.v1.authentication.secrets import login_checker,jwt_token_checker

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/comment", response_model=CommentResponse)
async def post_comment(request: CommentCreateRequest, response: Response, Authorization: str = Depends(login_checker)):
    try:
        decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
        email = decoded_payload.get("email")
        mobile_no = decoded_payload.get("mobile_number")

        if request.blog_id is None:
            response_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            response.status_code = response_status_code
            return CommentResponse(
                status=False,
                message="blog id is required",
                data=[],
                status_code=response_status_code,
            )

        if not any([email, mobile_no]):
            response.status_code = 422
            return CommentResponse(
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
            return CommentResponse(
                status=False,
                message="User not found",
                data=[],
                status_code=response.status_code,
            )

        new_comment = await sync_to_async(BlogComment.objects.create)(
            blog_post_id=request.blog_id, 
            user=user,
            content=request.content
        )

        response.status_code = 201
        return CommentResponse(
            status=True,
            message="Comment added successfully",
            data=[],
            status_code=response.status_code,
        )

    except Exception as e:
        logger.error(f"Unexpected Error While Posting Comments: {e}")
        response.status_code = 500

        return CommentResponse(
            status=False,
            message="An unexpected error occurred",
            data=[],  
            status_code=response.status_code,
        )
    

@router.get("/comments/{blog_id}", response_model=CommentResponse)
async def get_comments(blog_id: int, response: Response):
    try:
        comments = await sync_to_async(list)(
            BlogComment.objects.filter(blog_post_id=blog_id, deleted=False)
            .select_related("user")
            .order_by("created_at")
        )

        formatted_comments = []

        for comment in comments:
            username = "Anonymous"  
            if comment.user:
                user_details = await sync_to_async(UserPersonalDetails.objects.filter(user=comment.user).first)()
                if user_details and user_details.name:
                    username = user_details.name

            formatted_comments.append(
                CommentData(
                    id=comment.id,
                    user=username,
                    content=comment.content,
                    created_at=comment.created_at
                )
            )

        return CommentResponse(
            status=True,
            message="Comments retrieved successfully",
            data=formatted_comments,
            status_code=200
        )

    except Exception as e:
        response.status_code = 500
        return CommentResponse(
            status=False,
            message=f"Error: {str(e)}",
            data=[],
            status_code=response.status_code
        )

    
@router.put("/comment/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int,response:Response, request: CommentUpdateRequest, Authorization : str=Depends(login_checker)):
    try:
        decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
        email = decoded_payload.get("email")
        mobile_no = decoded_payload.get("mobile_number")

        if not any([email, mobile_no]):
            response.status_code = 422
            return CommentResponse(
                status=False,
                message="Invalid JWT token: no email or mobile number found.",
                data=[],
                status_code=response.status_code,
            )
        if email:
            user = await (UserContactInfo.objects.filter(email=email)).afirst()
        else:
            user = await (UserContactInfo.objects.filter(mobile_number=mobile_no)).afirst()

        if not user:
            response.status_code = 400
            return CommentResponse(
                status=False,
                message="User not found",
                data=[],
                status_code=response.status_code,
            )
        
        comment = await sync_to_async(BlogComment.objects.select_related('user').get)(
            id=comment_id, 
            deleted=False
        )

        if comment.user != user:
            response.status_code=403,
            return CommentResponse(
                status=False,
                message="You can only edit your own comments.",
                data=[],
                status_code=response.status_code,

            )

        comment.content = request.content
        await sync_to_async(comment.save)()
        response.status_code=200
        return CommentResponse(
            status=True,
            message="Comment updated successfully",
            data=[],
            status_code=response.status_code
        )
    
    except Exception as e:
        response.status_code=500
        return CommentResponse(
            status=False,
            message=f"Error: {str(e)}",
            data=[],
            status_code=response.status_code
        )

@router.delete("/comment/{comment_id}", response_model=CommentResponse)
async def delete_comment(comment_id: int, response:Response,Authorization: str=Depends(login_checker)):
    try:
        decoded_payload=jwt_token_checker(jwt_token=Authorization,encode=False)
        email=decoded_payload.get("email")
        mobile_no=decoded_payload.get("mobile_number")

        if not any([email, mobile_no]):
            response.status_code = 422
            return CommentResponse(
                status=False,
                message="Invalid JWT token: no email or mobile number found.",
                data=[],
                status_code=response.status_code,
            )
        
        if email:
            user=await (UserContactInfo.objects.filter(email=email)).afirst()
        else:
            user=await (UserContactInfo.objects.filter(mobile_number=mobile_no)).afirst()

        if not user:
            response.status_code = 400
            return CommentResponse(
                status=False,
                message="User not found",
                data=[],
                status_code=response.status_code,
            )

        comment = await sync_to_async(BlogComment.objects.select_related('user').get)(id=comment_id, deleted=False)

        if comment.user != user:
            response.status_code=403,
            return CommentResponse(
                status=False,
                message="You can only edit your own comments.",
                data=[],
                status_code=response.status_code,

            )
           
        comment.deleted = True  # Soft delete
        await sync_to_async(comment.save)()
        response.status_code=200
        return CommentResponse(
            status=True,
            message="Comment deleted successfully",
            data=[],
            status_code=response.status_code,
        )
    
    except BlogComment.DoesNotExist:
        response.status_code=404
        return CommentResponse(
            status=False,
            message="Comment not found",
            data=[],
            status_code=response.status_code,
        )
    
    except Exception as e:
        response.status_code=500
        return CommentResponse(
            status=False,
            message=f"Error: {str(e)}",
            data=[],
            status_code=response.status_code,
        )
