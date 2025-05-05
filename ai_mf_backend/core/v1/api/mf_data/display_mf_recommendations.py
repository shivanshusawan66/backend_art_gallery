from itertools import chain
from typing import Optional
from asgiref.sync import sync_to_async
from django.db.models.expressions import RawSQL
from django.apps import apps
from django.db.models import OuterRef, Subquery
from fastapi import APIRouter, Query, Response, status, Request, Depends, Header
from ai_mf_backend.models.v1.api.mf_recommendations import MFRecommendationsResponse
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.models.v1.database.mf_master_data import (
    MFSchemeMasterInDetails,
    MFSchemeMaster,
)
from ai_mf_backend.models.v1.database.mf_category_wise import (
    MutualFundSubcategory,
    MutualFundType,
)
from ai_mf_backend.models.v1.database.mf_filter_parameters import (
    MFFilterParameters,
    MFFilterColors,
)
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable
from ai_mf_backend.models.v1.database.questions import SectionWeightsPerUser
from ai_mf_backend.models.v1.database.mf_embedding_tables import (
    SectionWeightsPerMutualFund,
)
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    login_checker,
)

router = APIRouter()


@router.get(
    "/mf_recommendations",
    response_model=MFRecommendationsResponse,
    dependencies=[Depends(login_checker)],
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_mf_recommendations(
    request: Request,
    response: Response,
    page: int = Query(1, gt=0),
    page_size: int = Query(
        api_config.DEFAULT_PAGE_SIZE, ge=1, le=api_config.MAX_PAGE_SIZE
    ),
    sort_by: Optional[int] = Query(None, description="MF sorted by given id"),
    risk: Optional[int] = Query(None, description="MF filtered by risk"),
    investment_type: Optional[bool] = Query(
        None, description="MF filter by investment_type"
    ),
    fund_category_id: Optional[int] = Query(None),
    fund_subcategory_id: Optional[int] = Query(None),
    Authorization: str = Header(...),
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

        all_fields = api_config.MUTUAL_FUND_DASHBOARD_COLOUMNS
        all_markers = list(
            set(chain.from_iterable(api_config.COMPONENT_MARKER_MAP.values()))
        )

        refs = await sync_to_async(
            lambda: list(MFReferenceTable.objects.filter(marker_name__in=all_markers))
        )()

        marker_to_models = {
            ref.marker_name: apps.get_model(api_config.PROJECT_NAME, ref.table_name)
            for ref in refs
        }

        user_embedding = await sync_to_async(
            lambda: SectionWeightsPerUser.objects.get(user_id=user.user_id).embedding
        )()

        if hasattr(user_embedding, "tolist"):
            user_embedding_list = user_embedding.tolist()
        else:
            user_embedding_list = user_embedding

        active_schemecodes = await sync_to_async(
            lambda: set(
                MFSchemeMasterInDetails.objects.filter(status="Active").values_list(
                    "schemecode", flat=True
                )
            )
        )()

        base_query = MFSchemeMasterInDetails.objects.filter(
            schemecode__in=active_schemecodes
        )

        if "navrs_current" in marker_to_models:
            base_query = base_query.annotate(
                nav=Subquery(
                    marker_to_models["navrs_current"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("navrs")[:1]
                ),
                navdate=Subquery(
                    marker_to_models["navrs_current"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("navdate")[:1]
                ),
            )

        # Risk metrics
        if "jalpha_y" in marker_to_models:
            base_query = base_query.annotate(
                jalpha_y=Subquery(
                    marker_to_models["jalpha_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("jalpha_y")[:1]
                )
            )

        if "treynor_y" in marker_to_models:
            base_query = base_query.annotate(
                treynor_y=Subquery(
                    marker_to_models["treynor_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("treynor_y")[:1]
                )
            )

        if "beta_y" in marker_to_models:
            base_query = base_query.annotate(
                beta_y=Subquery(
                    marker_to_models["beta_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("beta_y")[:1]
                )
            )

        if "sd_y" in marker_to_models:
            base_query = base_query.annotate(
                sd_y=Subquery(
                    marker_to_models["sd_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("sd_y")[:1]
                )
            )

        if "sharpe_y" in marker_to_models:
            base_query = base_query.annotate(
                sharpe_y=Subquery(
                    marker_to_models["sharpe_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("sharpe_y")[:1]
                )
            )

        if "_1yrret" in marker_to_models:
            base_query = base_query.annotate(
                _1yrret=Subquery(
                    marker_to_models["_1yrret"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_1yrret")[:1]
                )
            )

        if "_3yearret" in marker_to_models:
            base_query = base_query.annotate(
                _3yearret=Subquery(
                    marker_to_models["_3yearret"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_3yearret")[:1]
                )
            )

        if "_5yearret" in marker_to_models:
            base_query = base_query.annotate(
                _5yearret=Subquery(
                    marker_to_models["_5yearret"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_5yearret")[:1]
                )
            )

        # Classification fields
        if "asset_type" in marker_to_models:
            base_query = base_query.annotate(
                asset_type=Subquery(
                    marker_to_models["asset_type"]
                    .objects.filter(classcode=OuterRef("classcode"))
                    .values("asset_type")[:1]
                )
            )

        if "category" in marker_to_models:
            base_query = base_query.annotate(
                category=Subquery(
                    marker_to_models["category"]
                    .objects.filter(classcode=OuterRef("classcode"))
                    .values("category")[:1]
                )
            )

        filter_kwargs = {}

        if fund_category_id is not None:
            filter_kwargs["asset_type"] = await sync_to_async(
                lambda: MutualFundType.objects.filter(id=fund_category_id)
                .values_list("fund_type", flat=True)
                .first()
            )()

        if fund_subcategory_id is not None:
            filter_kwargs["category"] = await sync_to_async(
                lambda: MutualFundSubcategory.objects.filter(id=fund_subcategory_id)
                .values_list("fund_subcategory", flat=True)
                .first()
            )()

        order_field = None
        if sort_by is not None:
            order_field = await sync_to_async(
                lambda: MFFilterParameters.objects.filter(id=sort_by)
                .values_list("parameter_name", flat=True)
                .first()
            )()

        risk_type = None
        if risk is not None:
            risk_type = await sync_to_async(
                lambda: MFFilterColors.objects.filter(id=risk)
                .values_list("color_name", flat=True)
                .first()
            )()
            filter_kwargs["color"] = risk_type

        if investment_type is not None:
            filter_kwargs["sip"] = "T" if investment_type else "F"

        if "navrs" in all_fields:
            all_fields.remove("navrs")

        mf_table = MFSchemeMasterInDetails._meta.db_table
        sw_table = SectionWeightsPerMutualFund._meta.db_table

        raw_sql = f"""
            (SELECT  sw.embedding <-> %s::vector
            FROM "{sw_table}" AS sw
            WHERE sw.scheme_code = "{mf_table}".schemecode
            LIMIT 1)
        """
        
        if filter_kwargs and order_field:
            similar_schemes = (
                base_query.annotate(similarity=RawSQL(raw_sql, (user_embedding_list,)))
                .filter(**filter_kwargs)
                .order_by("-similarity", order_field)
                .values(*all_fields,"schemecode","asset_type","category","nav","similarity")[:60]
            )
        elif filter_kwargs:
            similar_schemes = (
                base_query.annotate(similarity=RawSQL(raw_sql, (user_embedding_list,)))
                .filter(**filter_kwargs)
                .order_by("-similarity")
                .values(*all_fields,"schemecode","asset_type","category","nav","similarity")[:60]
            )
        else:
            similar_schemes = (
                base_query.annotate(similarity=RawSQL(raw_sql, (user_embedding_list,)))
                .order_by("-similarity")
                .values(*all_fields,"schemecode","asset_type","category","nav","similarity")[:60]
            )
        

        similar_schemes_list = await sync_to_async(lambda: list(similar_schemes))()

        full_results = similar_schemes_list

        total_count = len(full_results)
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size
        paginated_qs = full_results[offset : offset + page_size]

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