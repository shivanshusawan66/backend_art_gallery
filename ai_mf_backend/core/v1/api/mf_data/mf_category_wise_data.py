from fastapi import Response
from django.apps import apps
from django.db.models import OuterRef, Subquery, F

from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter

from fastapi import APIRouter, Query, Request, Response
from asgiref.sync import sync_to_async
from ai_mf_backend.utils.v1.api_projection.valid_fields import validate_query_params

from ai_mf_backend.models.v1.api.mf_category_wise import (
    MFCategoryOptionResponse,
    MFDataCategorySubcategoryWise,
    MFSubCategoryOptionResponse,
)
from ai_mf_backend.models.v1.database.mf_category_wise import (
    MutualFundSubcategory,
    MutualFundType,
)
from ai_mf_backend.models.v1.database.mf_master_data import MFSchemeMasterInDetails
from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable


router = APIRouter()


@router.get("/mf_options_fund_category", response_model=MFCategoryOptionResponse)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_mf_category_options(
    request: Request,
    response: Response,
):
    try:
        categories = await sync_to_async(list)(MutualFundType.objects.all())

        category_options = [
            {
                "key": int(category.id),
                "label": category.fund_type,
                "value": category.fund_type.lower(),
            }
            for category in categories
        ]

        data = {
            "fund_categories": {
                "name": "mf_category",
                "label": "MF Category",
                "options": category_options,
                "type": "dropdown",
                "default": [category_options[0]["key"]] if category_options else [],
                "required": False,
            }
        }

        response.status_code = 200
        return MFCategoryOptionResponse(
            status=True,
            message="Mutual Fund category options fetched successfully",
            data=data,
            status_code=response.status_code,
        )

    except Exception as e:
        response.status_code = 400
        return MFCategoryOptionResponse(
            status=False,
            message=f"Failed to fetch mutual fund category options: {str(e)}",
            data={},
            status_code=response.status_code,
        )


@router.get("/mf_options_fund_subcategory", response_model=MFSubCategoryOptionResponse)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_mf_subcategory_options(
    request: Request,
    response: Response,
    category_id: int = Query(..., ge=1, title="ID of the Fund Category"),
):
    try:
        category_instance = await sync_to_async(
            lambda: MutualFundType.objects.filter(deleted=False, id=category_id).first()
        )()

        if not category_instance:
            response.status_code = 404
            return MFSubCategoryOptionResponse(
                status=False,
                message=f"Category with ID {category_id} not found",
                data={},
                status_code=response.status_code,
            )

        subcategories = await sync_to_async(
            lambda: list(
                MutualFundSubcategory.objects.filter(fund_type_id=category_instance.id)
            )
        )()
        subcategory_options = [
            {
                "key": each_subcategory.id,
                "label": each_subcategory.fund_subcategory,
                "value": each_subcategory.fund_subcategory.lower(),
            }
            for each_subcategory in subcategories
        ]

        data = {
            "fund_category_type ": category_instance.fund_type,
            "fund_subcategories": subcategory_options,
        }

        response.status_code = 200
        return MFSubCategoryOptionResponse(
            status=True,
            message="Successfully fetched mutual fund category options",
            data=data,
            status_code=response.status_code,
        )

    except Exception as e:
        response.status_code = 400
        return MFSubCategoryOptionResponse(
            status=False,
            message=f"Failed to fetch mutual fund category options: {str(e)}",
            data={},
            status_code=response.status_code,
        )


@router.get(
    "/get_fund_data_category_subcategory_wise",
    response_model=MFDataCategorySubcategoryWise,
    deprecated=True,
    tags=["Deprecated"],
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def fund_data_category_subcategory_wise(
    request: Request,
    response: Response,
    fund_category_id: int = Query(default=None, description="category id of fund"),
    fund_subcategory_id: int = Query(
        default=None, description="subcategory id of category"
    ),
    page: int = Query(1, gt=0),
    page_size: int = Query(
        api_config.DEFAULT_PAGE_SIZE, ge=1, le=api_config.MAX_PAGE_SIZE
    ),
):
    allowed_params = ["fund_category_id", "fund_subcategory_id", "page", "page_size"]

    try:
        validate_query_params(dict(request.query_params), allowed_params)

        marker_list = ["navrs", "_1yrret", "asset_type", "category"]

        fund_category_name = await sync_to_async(
            lambda: MutualFundType.objects.filter(id=fund_category_id)
            .values_list("fund_type", flat=True)
            .first()
        )()

        fund_subcategory_name = await sync_to_async(
            lambda: MutualFundSubcategory.objects.filter(id=fund_subcategory_id)
            .values_list("fund_subcategory", flat=True)
            .first()
        )()

        filter_kwargs = {}

        if fund_category_id:
            filter_kwargs["asset_type"] = await sync_to_async(
                lambda: MutualFundType.objects.filter(id=fund_category_id)
                .values_list("fund_type", flat=True)
                .first()
            )()
        if fund_subcategory_id:
            filter_kwargs["category"] = await sync_to_async(
                lambda: MutualFundSubcategory.objects.filter(id=fund_subcategory_id)
                .values_list("fund_subcategory", flat=True)
                .first()
            )()

        refs = await sync_to_async(
            lambda: list(MFReferenceTable.objects.filter(marker_name__in=marker_list))
        )()

        marker_to_models = {
            ref.marker_name: apps.get_model(api_config.PROJECT_NAME, ref.table_name)
            for ref in refs
            if ref.marker_name in marker_list
        }

        active_schemecode = await sync_to_async(list)(
            MFSchemeMasterInDetails.objects.filter(status="Active").values_list(
                "schemecode", flat=True
            )
        )

        base_query = MFSchemeMasterInDetails.objects.filter(
            schemecode__in=active_schemecode
        )

        if "navrs" in marker_to_models:
            base_query = base_query.annotate(
                navrs=Subquery(
                    marker_to_models["navrs"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("navrs")[:1]
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

        filtered_query = base_query.filter(**filter_kwargs).order_by(
            F("_1yrret").desc(nulls_last=True)
        )

        result_query = filtered_query.values("schemecode", "s_name", "_1yrret", "navrs")

        full_results = await sync_to_async(lambda: list(result_query))()

        total_count = len(full_results)
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size
        paginated_qs = full_results[offset : offset + page_size]

        response.status_code = 200
        return MFDataCategorySubcategoryWise(
            status=True,
            message="Success",
            page=page,
            total_pages=total_pages,
            total_data=total_count,
            data=paginated_qs,
            fund_category=fund_category_name,
            fund_subcategory=fund_subcategory_name,
            status_code=response.status_code,
        )
    except ValueError as e:
        response.status_code = 400
        return MFDataCategorySubcategoryWise(
            status=False,
            message=str(e),
            page=0,
            total_pages=0,
            total_data=0,
            data=[],
            status_code=response.status_code,
        )
