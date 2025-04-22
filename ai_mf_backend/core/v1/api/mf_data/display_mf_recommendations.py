from asgiref.sync import sync_to_async
from django.db.models.expressions import RawSQL
from django.apps import apps
from fastapi import APIRouter, Query, Response, status, Request ,Depends,Header
from ai_mf_backend.models.v1.api.mf_recommendations import MFRecommendationsResponse
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.models.v1.database.user import (
    UserContactInfo
)
from ai_mf_backend.models.v1.database.mf_reference_table import(
    MFReferenceTable
)
from ai_mf_backend.models.v1.database.questions import(
    SectionWeightsPerUser
)
from ai_mf_backend.models.v1.database.mf_embedding_tables import(
    SectionWeightsPerMutualFund
)
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    login_checker,
)

router = APIRouter()

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/mf_recommendations", response_model=MFRecommendationsResponse ,dependencies=[Depends(login_checker)],)
async def get_high_return_funds(
    request: Request,
    response: Response,
    page: int = Query(1, gt=0),
    page_size: int = Query(api_config.DEFAULT_PAGE_SIZE, ge=1, le=api_config.MAX_PAGE_SIZE),
    Authorization: str = Header(...)
):
    
    decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
    email = decoded_payload.get("email")
    mobile_number = decoded_payload.get("mobile_number")

    if not any([email, mobile_number]):
        response.status_code = 422
        return MFRecommendationsResponse(
            status=False,
            message="Invalid JWT token: no email or mobile number found.",
            data={},
            status_code=422,
        )

    if email:
        user = await sync_to_async(
            UserContactInfo.objects.filter(email=email).first
        )()
    else:
        user = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=mobile_number).first
        )()

    if not user:
        response.status_code = 400
        return MFRecommendationsResponse(
            status=False,
            message="User not found",
            data={},
            status_code=400,
        )
    
    marker_list = ["asset_type", "_1yrret","navrs"]


    refs = await sync_to_async(lambda: list(MFReferenceTable.objects.filter(marker_name__in=marker_list)))()

    marker_to_models = {
        ref.marker_name: apps.get_model(api_config.PROJECT_NAME,ref.table_name)
        for ref in refs
        if ref.marker_name in marker_list
    }

    user_embedding = await sync_to_async(
        lambda: SectionWeightsPerUser.objects.get(user_id=user.user_id).embedding
    )()

    if hasattr(user_embedding, "tolist"):
        user_embedding_list = user_embedding.tolist()
    else:
        user_embedding_list = user_embedding

    similar_funds = await sync_to_async(
        lambda: list(SectionWeightsPerMutualFund.objects.annotate(
            similarity=RawSQL(
                "embedding <=> %s::vector", 
                (user_embedding_list,)
            )
        ).order_by('-similarity'))
    )()

    recommendations = []
    for fund in similar_funds:
        fund_embedding = fund.embedding
        if hasattr(fund_embedding, "tolist"):
            fund_embedding = fund_embedding.tolist()
        
        recommendations.append({
            'scheme_code': fund.scheme_code,
            'similarity_score': 1 - fund.similarity,
            'embedding': fund_embedding
        })

    total_count = len(recommendations)
    print(total_count)
    total_pages = (total_count + page_size - 1) // page_size
    print(total_pages)
    offset = (page - 1) * page_size
    print(offset)
    print(page)
    print("page size: ",page_size)
    paginated_qs = recommendations[offset: offset + page_size]
    print(paginated_qs)

    response.status_code = status.HTTP_200_OK
    return MFRecommendationsResponse(
            status=True,
            message="Success",
            page=page,
            total_pages=total_pages,
            total_data=total_count,
            data=paginated_qs,
            status_code=200,
        )