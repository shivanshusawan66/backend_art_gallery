from asgiref.sync import sync_to_async
from django.db.models.expressions import RawSQL
from django.apps import apps
from django.db.models import OuterRef, Subquery
from fastapi import APIRouter, Query, Response, status, Request ,Depends,Header
from ai_mf_backend.models.v1.api.mf_recommendations import MFRecommendationsResponse
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *
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
    try:
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
        
        marker_list = ["asset_type", "_1yrret","navrs_current"]


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
    
        active_schemecodes = await sync_to_async(
            lambda: set(MFSchemeMasterInDetails.objects.filter(
                status="Active"
            ).values_list("schemecode", flat=True))
        )()

        base_query = MFSchemeMasterInDetails.objects.filter(schemecode__in=active_schemecodes)

        if "_1yrret" in marker_to_models:
            base_query = base_query.annotate(
                _1yrret=Subquery(
                    marker_to_models["_1yrret"].objects.filter(
                        schemecode=OuterRef("schemecode")
                    ).values("_1yrret")[:1]
                )
            )

        if "navrs_current" in marker_to_models:
            base_query = base_query.annotate(
                navrs=Subquery(
                    marker_to_models["navrs_current"].objects.filter(
                        schemecode=OuterRef("schemecode")
                    ).values("navrs")[:1]
                )
            )

        if "asset_type" in marker_to_models:
            base_query = base_query.annotate(
                asset_type=Subquery(
                    marker_to_models["asset_type"].objects.filter(
                        classcode=OuterRef("classcode")
                    ).values("asset_type")[:1]
                )
            )

        mf_table = MFSchemeMasterInDetails._meta.db_table
        sw_table = SectionWeightsPerMutualFund._meta.db_table

        raw_sql = f"""
            (SELECT  sw.embedding <-> %s::vector
            FROM "{sw_table}" AS sw
            WHERE sw.scheme_code = "{mf_table}".schemecode
            LIMIT 1)
        """

        base_query = base_query.annotate(
            similarity=RawSQL(raw_sql, (user_embedding_list,))
        ).order_by("similarity")


        result_query = base_query.values("schemecode", "navrs", "_1yrret", "asset_type", "s_name","similarity")
        full_results = await sync_to_async(lambda: list(result_query))()

        total_count = len(full_results)
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size
        paginated_qs = full_results[offset: offset + page_size]

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
    
    except Exception as e:
        response.status_code = 400
        return MFRecommendationsResponse(
            status=False,
            message=f"Error occurred: {str(e)}",
            page=0,
            total_pages=0,
            total_data=0,
            data=[],
            status_code=400,
        ) 