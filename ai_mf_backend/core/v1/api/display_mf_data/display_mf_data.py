from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Dict, List, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from ai_mf_backend.models.v1.api.display_mf_data import (
    AnnualReturnModel,
    ComprehensiveFundDataModel,
    FilteredFundsResponse,
    FundDataModel,
    FundFamiliesResponseModel,
    FundFilterRequest,
    FundOverviewModel,
    FundRequestModel,
    HistoricalDataModel,
    HistoricalDataRequestModel,
    HistoricalDataResponseModel,
    MutualFundModel,
    PaginatedRequestModel,
    PerformanceDataModel,
    RiskStatisticsModel,
    TrailingReturnModel,
)
from ai_mf_backend.models.v1.database.mutual_fund import (
    AnnualReturn,
    FundData,
    FundOverview,
    HistoricalData,
    MutualFund,
    PerformanceData,
    RiskStatistics,
    TrailingReturn,
)
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.db.models import Q

router = APIRouter()


def paginate(items: List, page: int, page_size: int):
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]

    return {
        "items": paginated_items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# Pydantic model for paginated request
# Define PaginatedResponseModel as a Pydantic model
class PaginatedResponseModel(BaseModel):
    status: str
    items: List[MutualFundModel]
    total: int
    page: int
    page_size: int
    # Adding a status field to the response body


@router.post("/mutual-funds/", response_model=PaginatedResponseModel)
async def read_mutual_funds(pagination: PaginatedRequestModel):
    page = pagination.page
    page_size = pagination.page_size

    try:
        # Using sync_to_async to fetch data in an async context
        mutual_funds = await sync_to_async(list)(MutualFund.objects.all())
    except DatabaseError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching mutual funds",
        )

    # Use the paginate function to get the paginated data
    paginated = paginate(mutual_funds, page, page_size)

    if not paginated["items"]:  # Check if items is empty
        raise HTTPException(status_code=404, detail="No mutual funds found")

    # Construct the response with pagination info
    response_data = PaginatedResponseModel(
        status="200",
        items=paginated["items"],
        total=paginated["total"],
        page=page,
        page_size=page_size,
    )

    return response_data  # Directly return the response model


# API to retrieve comprehensive fund data, accepting JSON payload for fund_id
@router.post("/fund_data with fund_id/", response_model=ComprehensiveFundDataModel)
async def read_fund_data(fund_request: FundRequestModel):
    fund_id = fund_request.fund_id

    try:
        # Fetching mutual fund details
        mutual_fund = await sync_to_async(MutualFund.objects.get)(id=fund_id)
    except ObjectDoesNotExist:
        raise HTTPException(
            status_code=404, detail=f"Mutual Fund with ID '{fund_id}' not found"
        )
    except DatabaseError:
        raise HTTPException(
            status_code=500, detail="Database error occurred while fetching fund data"
        )

    # Fetching related data
    fund_overview = await sync_to_async(
        FundOverview.objects.filter(fund_id=fund_id).first
    )()
    performance_data = await sync_to_async(list)(
        PerformanceData.objects.filter(fund_id=fund_id)
    )
    trailing_returns = await sync_to_async(list)(
        TrailingReturn.objects.filter(fund_id=fund_id)
    )
    annual_returns = await sync_to_async(list)(
        AnnualReturn.objects.filter(fund_id=fund_id)
    )
    fund_data = await sync_to_async(FundData.objects.filter(fund_id=fund_id).first)()
    risk_statistics = await sync_to_async(list)(
        RiskStatistics.objects.filter(fund_id=fund_id)
    )

    # Constructing the response model with serialization
    return ComprehensiveFundDataModel(
        mutual_fund=MutualFundModel.from_orm(mutual_fund),  # Convert to Pydantic model
        fund_overview=(
            FundOverviewModel.from_orm(fund_overview) if fund_overview else None
        ),  # Convert if exists
        performance_data=[
            PerformanceDataModel.from_orm(pd) for pd in performance_data
        ],  # Convert each instance
        trailing_returns=[
            TrailingReturnModel.from_orm(tr) for tr in trailing_returns
        ],  # Convert each instance
        annual_returns=[
            AnnualReturnModel.from_orm(ar) for ar in annual_returns
        ],  # Convert each instance
        fund_data=(
            FundDataModel.from_orm(fund_data) if fund_data else None
        ),  # Convert if exists
        risk_statistics=[
            RiskStatisticsModel.from_orm(rs) for rs in risk_statistics
        ],  # Convert each instance
    )


@router.post(
    "/mutual-funds/historical-data", response_model=HistoricalDataResponseModel
)
async def read_historical_data_by_fund_id(request: HistoricalDataRequestModel):
    fund_id = request.fund_id
    page = request.page
    page_size = request.page_size

    try:
        # Fetch the mutual fund object asynchronously
        mutual_fund = await sync_to_async(MutualFund.objects.get)(id=fund_id)
    except MutualFund.DoesNotExist:
        raise HTTPException(
            status_code=404, detail=f"Mutual Fund with ID '{fund_id}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Fetch historical data for the mutual fund asynchronously
    historical_data_queryset = mutual_fund.historical_data.all()
    historical_data_list = await sync_to_async(list)(historical_data_queryset)

    # Check if data is available
    if not historical_data_list:
        return HistoricalDataResponseModel(status_code=404, historical_data=[])

    # Prepare the response data
    historical_data = [
        HistoricalDataModel(
            id=data.id,
            fund_id=data.fund_id,
            date=data.date,
            open=data.open,
            high=data.high,
            low=data.low,
            close=data.close,
            adj_close=data.adj_close,
            volume=data.volume,
        )
        for data in historical_data_list
    ]

    return HistoricalDataResponseModel(status_code=200, historical_data=historical_data)


@router.get(
    "/fund-families-morningstar-rating/", response_model=FundFamiliesResponseModel
)
async def get_fund_families():
    try:
        # Fetch distinct fund family names and Morningstar ratings
        fund_families = await sync_to_async(list)(
            FundOverview.objects.values_list("fund_family", flat=True).distinct()
        )
        morningstar_ratings = await sync_to_async(list)(
            FundOverview.objects.values_list("morningstar_rating", flat=True).distinct()
        )

        # If no data found, return 404 error
        if not fund_families and not morningstar_ratings:
            return FundFamiliesResponseModel(
                status_code=404, fund_family=[], morningstar_ratings=[]
            )

        # Return the distinct lists with status code 200
        return FundFamiliesResponseModel(
            status_code=200,
            fund_family=fund_families,
            morningstar_ratings=morningstar_ratings,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching fund families and ratings",
        )


@router.post("/mutual-funds/filter", response_model=FilteredFundsResponse)
async def filter_mutual_funds(filter_request: FundFilterRequest):
    try:
        query = MutualFund.objects.select_related("overview", "fund_data")
        filters = Q()
        applied_filters = []

        # Build filter conditions using AND operations
        if (
            filter_request.fund_family
            and filter_request.fund_family.lower() != "string"
        ):
            filters &= Q(overview__fund_family__iexact=filter_request.fund_family)
            applied_filters.append(f"fund_family: {filter_request.fund_family}")

        # Updated Morningstar rating handling
        if (
            filter_request.morningstar_rating
            and filter_request.morningstar_rating.lower() != "string"
        ):
            # Count stars or get numeric value
            if "*" in filter_request.morningstar_rating:
                star_count = filter_request.morningstar_rating.count("*")
                star_filter = "*" * star_count
            else:
                try:
                    star_count = int(filter_request.morningstar_rating.strip())
                    star_filter = "*" * star_count
                except ValueError:
                    star_count = 0
                    star_filter = ""

            # Only apply filter if star_count is valid (1-5)
            if 1 <= star_count <= 5:
                filters &= Q(overview__morningstar_rating__exact=star_filter)
                applied_filters.append(f"morningstar_rating: {star_count} stars")

        # Handle investment range filters
        if filter_request.min_investment_range_start is not None:
            if filter_request.min_investment_range_start > Decimal("0"):
                filters &= Q(
                    fund_data__min_initial_investment__gte=filter_request.min_investment_range_start
                )
                applied_filters.append(
                    f"min_investment_start: {float(filter_request.min_investment_range_start)}"
                )

        if filter_request.min_investment_range_end is not None:
            if filter_request.min_investment_range_end > Decimal("0"):
                filters &= Q(
                    fund_data__min_initial_investment__lte=filter_request.min_investment_range_end
                )
                applied_filters.append(
                    f"min_investment_end: {float(filter_request.min_investment_range_end)}"
                )

        # Apply filters
        base_query = query.filter(filters) if filters != Q() else query

        # For debugging: Print the generated SQL query
        print("Generated SQL:", base_query.query)
        print("Applied Filters:", applied_filters)

        # Get total count
        total_count = await sync_to_async(base_query.count)()

        if total_count == 0:
            # Convert request dict to JSON serializable format
            filter_dict = {
                key: float(value) if isinstance(value, Decimal) else value
                for key, value in filter_request.dict().items()
            }

            # Get available ratings for debugging
            available_ratings = await sync_to_async(list)(
                FundOverview.objects.values_list(
                    "morningstar_rating", flat=True
                ).distinct()
            )

            raise HTTPException(
                status_code=404,
                detail={
                    "message": "No mutual funds found matching the specified criteria",
                    "applied_filters": applied_filters,
                    "total_funds_in_db": await sync_to_async(
                        MutualFund.objects.count
                    )(),
                    "available_fund_families": await sync_to_async(list)(
                        FundOverview.objects.values_list(
                            "fund_family", flat=True
                        ).distinct()
                    ),
                    "available_ratings": available_ratings,  # Added for debugging
                },
            )

        # Calculate pagination
        total_pages = (
            total_count + filter_request.page_size - 1
        ) // filter_request.page_size
        start_idx = (filter_request.page - 1) * filter_request.page_size
        end_idx = start_idx + filter_request.page_size

        # Get paginated funds
        paginated_funds = await sync_to_async(list)(base_query[start_idx:end_idx])

        # Fetch comprehensive data for each fund
        comprehensive_funds = []
        for fund in paginated_funds:
            try:
                # Fetch all related data
                performance_data = await sync_to_async(list)(
                    PerformanceData.objects.filter(fund_id=fund.id)
                )
                trailing_returns = await sync_to_async(list)(
                    TrailingReturn.objects.filter(fund_id=fund.id)
                )
                annual_returns = await sync_to_async(list)(
                    AnnualReturn.objects.filter(fund_id=fund.id)
                )
                risk_statistics = await sync_to_async(list)(
                    RiskStatistics.objects.filter(fund_id=fund.id)
                )

                # Create comprehensive fund data model
                comprehensive_fund = ComprehensiveFundDataModel(
                    mutual_fund=MutualFundModel.from_orm(fund),
                    fund_overview=(
                        FundOverviewModel.from_orm(fund.overview)
                        if hasattr(fund, "overview")
                        else None
                    ),
                    performance_data=[
                        PerformanceDataModel.from_orm(pd) for pd in performance_data
                    ],
                    trailing_returns=[
                        TrailingReturnModel.from_orm(tr) for tr in trailing_returns
                    ],
                    annual_returns=[
                        AnnualReturnModel.from_orm(ar) for ar in annual_returns
                    ],
                    fund_data=(
                        FundDataModel.from_orm(fund.fund_data)
                        if hasattr(fund, "fund_data")
                        else None
                    ),
                    risk_statistics=[
                        RiskStatisticsModel.from_orm(rs) for rs in risk_statistics
                    ],
                )
                comprehensive_funds.append(comprehensive_fund)

            except Exception as e:
                continue

        return FilteredFundsResponse(
            status_code=200,  # Adding status code 200
            total_count=total_count,
            funds=comprehensive_funds,
            current_page=filter_request.page,
            total_pages=total_pages,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        # Convert request dict to JSON serializable format
        try:
            filter_dict = {
                key: float(value) if isinstance(value, Decimal) else value
                for key, value in filter_request.dict().items()
            }
        except:
            filter_dict = str(filter_request)

        raise HTTPException(
            status_code=500,
            detail={
                "message": f"An error occurred while filtering mutual funds: {str(e)}",
                "applied_filters": (
                    applied_filters if "applied_filters" in locals() else []
                ),
                "filter_request": filter_dict,
            },
        )
