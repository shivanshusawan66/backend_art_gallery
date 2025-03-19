from fastapi import APIRouter, Depends, HTTPException
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.database.blog import BlogComment
from ai_mf_backend.models.v1.database.user import UserContactInfo
from django.db.models import Q
from ai_mf_backend.models.v1.database.user import UserPersonalDetails

from ai_mf_backend.models.v1.api.blog_comment import (
    CommentResponse, CommentData, CommentCreateRequest, CommentUpdateRequest
)
from ai_mf_backend.utils.v1.authentication.secrets import login_checker,jwt_token_checker

router = APIRouter()

@router.post("/comment", response_model=CommentResponse)
async def post_comment(request: CommentCreateRequest, Authorization: str = Depends(login_checker)):
    try:

        decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
        email = decoded_payload.get("email")
        mobile_no = decoded_payload.get("mobile_number")

        if not any([email, mobile_no]):
            raise HTTPException(status_code=400, detail="Invalid token: No email or mobile number found.")
        
        
        if email:
            user = await (UserContactInfo.objects.filter(email=email)).afirst()
        else:
            user = await (UserContactInfo.objects.filter(mobile_number=mobile_no)).afirst()
       

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        
        new_comment = await sync_to_async(BlogComment.objects.create)(
            blog_post_id=request.blog_id, 
            user=user,
            content=request.content
        )

        return CommentResponse(
            status=True,
            message="Comment added successfully",
            data=[],
            status_code=201
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/comments/{blog_id}", response_model=CommentResponse)
async def get_comments(blog_id: int):
    try:
        
        comments = await sync_to_async(list)(
            BlogComment.objects.filter(blog_post_id=blog_id, deleted=False)
            .select_related("user")  
            .order_by("created_at")
        )

        formatted_comments = []

        for comment in comments:
            
            

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
        return CommentResponse(
            status=False,
            message=f"Error: {str(e)}",
            data=[],
            status_code=500
        )
@router.put("/comment/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, request: CommentUpdateRequest, Authorization : str=Depends(login_checker)):
    try:
        decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
        email = decoded_payload.get("email")
        mobile_no = decoded_payload.get("mobile_number")

        if not any([email, mobile_no]):
             raise HTTPException(status_code=400, detail="Invalid token : No email or mobile number found.")
        
        if email:
            user = await (UserContactInfo.objects.filter(email=email)).afirst()
        else:
            user = await (UserContactInfo.objects.filter(mobile_number=mobile_no)).afirst()

        if not user:
             raise HTTPException(status_code=404, detail="User not found.")

        
        comment = await sync_to_async(BlogComment.objects.select_related('user').get)(
            id=comment_id, 
            deleted=False
        )

        if comment.user != user:
            raise HTTPException(status_code=403, detail="You can only edit your own comments.")

        comment.content = request.content
        await sync_to_async(comment.save)()

        return CommentResponse(
            status=True,
            message="Comment updated successfully",
            data=[],
            status_code=200
        )
    
    except BlogComment.DoesNotExist:
        return CommentResponse(
            status=False,
            message="Comment not found",
            data=[],
            status_code=404
        )
    
    except Exception as e:
        return CommentResponse(
            status=False,
            message=f"Error: {str(e)}",
            data=[],
            status_code=500
        )

@router.delete("/comment/{comment_id}", response_model=CommentResponse)
async def delete_comment(comment_id: int, Authorization: str=Depends(login_checker)):
    try:
        decoded_payload=jwt_token_checker(jwt_token=Authorization,encode=False)
        email=decoded_payload.get("email")
        mobile_no=decoded_payload.get("mobile_number")

        if not any([email,mobile_no]):
            raise HTTPException(status_code=400,detail="Invalid token : No email or mobile number found.")
        
        if email:
            user=await (UserContactInfo.objects.filter(email=email)).afirst()
        else:
            user=await (UserContactInfo.objects.filter(mobile_number=mobile_no)).afirst()

        if not user:
            raise HTTPException(status_code=404,detail="User not found.")

        comment = await sync_to_async(BlogComment.objects.select_related('user').get)(id=comment_id, deleted=False)

        if comment.user != user:
            raise HTTPException(status_code=403, detail="You can only delete your own comments.")

        comment.deleted = True  # Soft delete
        await sync_to_async(comment.save)()

        return CommentResponse(
            status=True,
            message="Comment deleted successfully",
            data=[],
            status_code=200
        )
    
    except BlogComment.DoesNotExist:
        return CommentResponse(
            status=False,
            message="Comment not found",
            data=[],
            status_code=404
        )
    
    except Exception as e:
        return CommentResponse(
            status=False,
            message=f"Error: {str(e)}",
            data=[],



            status_code=500
        )
