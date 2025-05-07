import logging
from fastapi import APIRouter, Request, Response
from asgiref.sync import sync_to_async

from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.models.v1.database.user_review import UserReview
from ai_mf_backend.models.v1.api.user_review import UserReviewResponse


router = APIRouter(tags=["user_review"])
logger = logging.getLogger(__name__)


@router.get(
    "/get_user_review",
    response_model=UserReviewResponse,
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_user_review(request: Request, response: Response):
    try:
        user_reviews = await sync_to_async(list)(
            UserReview.objects.filter(deleted=False).all()
        )

        if not user_reviews:
            return UserReviewResponse(
                status=False, message="No user reviews found.", data=[], status_code=404
            )

        reviews_data = [
            {
                "id": review.id,
                "username": review.username,
                "designation": review.designation,
                "review_title": review.review_title,
                "review_body": review.review_body,
                "number_of_stars": review.number_of_stars,
                "location": review.location,
                "user_image": review.user_image.name if review.user_image else None,
            }
            for review in user_reviews
        ]

        return UserReviewResponse(
            status=True,
            message="User reviews fetched successfully",
            data=reviews_data,
            status_code=200,
        )

    except Exception as e:
        logger.error(f"Error fetching user reviews: {str(e)}")
        response.status_code = 500
        return UserReviewResponse(
            status=False,
            message=f"Failed to fetch user reviews: {str(e)}",
            data=None,
            status_code=500,
        )
