from fastapi import APIRouter, Depends, Request, Query
from asgiref.sync import sync_to_async
from typing import Optional


from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.config.v1.mutual_fund_tables_config import mutual_funds_table_config
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.models.v1.database.mutual_fund import (
    MutualFund,
    AnnualReturn,
    PerformanceData,
    RiskStatistics,
    TrailingReturn,
    HistoricalData,
)
from ai_mf_backend.models.v1.api.display_each_mf import (
    CustomMutualFundOverviewCustomResponse,
    PerformanceDataCustomResponse,
    RiskStatisticsResponseData,
    RiskStatisticsObject,
    RiskStatisticsCustomResponse,
    TrailingReturnResponseData,
    TrailingReturnObject,
    TrailingReturnCustomResponse,
    HistoricalDataResponseData,
    HistoricalDataObject,
    HistoricalDataCustomResponse,
    AnnualReturnResponseData,
    AnnualReturnObject,
    AnnualReturnCustomResponse,
)
from ai_mf_backend.utils.v1.display_fund_data.display_each import process_fields, process_years
from ai_mf_backend.utils.v1.validators.input import validate_fund_id


router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_overview/{fund_id}")
async def get_overview(
    request: Request,
    fund_id: int = Depends(validate_fund_id),
    fields: Optional[str] = Query(
        default=None, description="Comma-separated list of fields to include"
    ),
):

    all_fields = mutual_funds_table_config.MUTUAL_FUND_OVERVIEW_COLOUMNS

    try:

        fields_to_project = process_fields(fields, all_fields)
    except ValueError as e:
        return CustomMutualFundOverviewCustomResponse(
            status=False,
            message=str(e),
            data={},
            status_code=400,
        )
    try:

        fund_overview = await sync_to_async(
            MutualFund.objects.only(*fields_to_project).get
        )(id=fund_id)

        response_data = {
            field: getattr(fund_overview, field, None) for field in fields_to_project
        }

        return CustomMutualFundOverviewCustomResponse(
            status=True,
            message=f"Fund with ID {fund_id} found",
            data=response_data,
            status_code=200,
        )
    except MutualFund.DoesNotExist:
        return CustomMutualFundOverviewCustomResponse(
            status=False,
            message=f"No fund found for fund ID {fund_id}",
            data={},
            status_code=404,
        )
    except Exception as e:
        return CustomMutualFundOverviewCustomResponse(
            status=False,
            message=f"Error occured while retriving fund overview data for mutual fund with id {fund_id}, {str(e)}",
            data={},
            status_code=400,
        )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_performance/{fund_id}")
async def get_performance(
    request: Request,
    fund_id: int = Depends(validate_fund_id),
    fields: Optional[str] = Query(
        default=None, description="Comma-separated list of fields to include"
    ),
):

    all_fields = mutual_funds_table_config.MUTUAL_FUND_PERFORMANCE_COLOUMNS

    try:

        fields_to_project = process_fields(fields, all_fields)
    except ValueError as e:
        
        return PerformanceDataCustomResponse(
            
            status=False,
            message=str(e),
            data={},
            status_code=400,
        )
    try:
        performance = await sync_to_async(
            PerformanceData.objects.only(*fields_to_project).get
        )(fund_id=fund_id)

        response_data = {
            field: getattr(performance, field, None) for field in fields_to_project
        }

        return PerformanceDataCustomResponse(
            status=True,
            message=f"Fund with ID {fund_id} found",
            data=response_data,
            status_code=200,
        )
    except PerformanceData.DoesNotExist:
        return PerformanceDataCustomResponse(
            status=False,
            message=f"No fund found for fund ID {fund_id}",
            data={},
            status_code=404,
        )
    except Exception as e:
        return PerformanceDataCustomResponse(
            status=False,
            message=f"Error occured while retriving performance data for mutual fund with id {fund_id}, {str(e)}",
            data={},
            status_code=400,
        )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_annual_return/{fund_id}")
async def get_annual_returns(
    request: Request, 
    fund_id: int = Depends(validate_fund_id),
    years: Optional[str] =  Query(default=None, description="Comma-seperated list of years")
):
    all_years = mutual_funds_table_config.MUTUAL_FUND_ANNUAL_RETURNS_YEARS
    try:

        years_to_project = process_years(years, all_years)
    except ValueError as e:
        
        return AnnualReturnCustomResponse(
            
            status=False,
            message=str(e),
            data={},
            status_code=400,
        )
    try:
        annual_returns = await sync_to_async(list)(
            AnnualReturn.objects.filter(fund_id=fund_id, year__in = years_to_project)
        )
        if not annual_returns:
            return AnnualReturnCustomResponse(
                status=False,
                message=f"No fund found for fund ID {fund_id}",
                data={},
                status_code=404,
            )
        response_data = AnnualReturnResponseData(
            fund_id=fund_id,
            annual_returns=[
                AnnualReturnObject(year=ar.year, fund_return=ar.fund_return)
                for ar in annual_returns
            ],
        ).model_dump()

        return AnnualReturnCustomResponse(
            status=True,
            message=f"Fund with ID {fund_id} found",
            data=response_data,
            status_code=200,
        )
    except Exception as e:
        return AnnualReturnCustomResponse(
            status=False,
            message=f"Error occured while retriving annual return data for mutual fund with id {fund_id}, {str(e)}",
            data={},
            status_code=400,
        )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_risk_statistics/{fund_id}")
async def get_risk_statistics(
    request: Request, fund_id: int = Depends(validate_fund_id)
):
    try:
        risk_statistics = await sync_to_async(list)(
            RiskStatistics.objects.filter(fund_id=fund_id)
        )
        if not risk_statistics:
            return RiskStatisticsCustomResponse(
                status=False,
                message=f"No fund found for fund ID {fund_id}",
                data={},
                status_code=404,
            )
        response_data = RiskStatisticsResponseData(
            fund_id=fund_id,
            risk_statistics=[
                RiskStatisticsObject(
                    period=rs.period,
                    alpha=rs.alpha,
                    beta=rs.beta,
                    mean_annual_return=rs.mean_annual_return,
                    r_squared=rs.r_squared,
                    standard_deviation=rs.standard_deviation,
                    sharpe_ratio=rs.sharpe_ratio,
                    treynor_ratio=rs.treynor_ratio,
                )
                for rs in risk_statistics
            ],
        ).model_dump()

        return RiskStatisticsCustomResponse(
            status=True,
            message=f"Fund with ID {fund_id} found",
            data=response_data,
            status_code=200,
        )
    except Exception as e:
        return RiskStatisticsCustomResponse(
            status=False,
            message=f"Error occured while retriving risk statistics data for mutual fund with id {fund_id}, {str(e)}",
            data={},
            status_code=400,
        )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_trailing_return/{fund_id}")
async def get_trailing_return(
    request: Request, fund_id: int = Depends(validate_fund_id)
):
    try:
        trailing_return = await sync_to_async(list)(
            TrailingReturn.objects.filter(fund_id=fund_id)
        )
        if not trailing_return:
            return TrailingReturnCustomResponse(
                status=False,
                message=f"No fund found for fund ID {fund_id}",
                data={},
                status_code=404,
            )
        response_data = TrailingReturnResponseData(
            fund_id=fund_id,
            trailing_return=[
                TrailingReturnObject(
                    metric=tr.metric,
                    fund_return=tr.fund_return,
                    benchmark_return=tr.benchmark_return,
                )
                for tr in trailing_return
            ],
        ).model_dump()
        return TrailingReturnCustomResponse(
            status=True,
            message=f"Fund with ID {fund_id} found",
            data=response_data,
            status_code=200,
        )
    except Exception as e:
        return TrailingReturnCustomResponse(
            status=False,
            message=f"Error occured while retriving trailing return data for mutual fund with id {fund_id}, {str(e)}",
            data={},
            status_code=400,
        )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_historical_data/{fund_id}")
async def get_historical_data(
    request: Request, fund_id: int = Depends(validate_fund_id)
):
    try:
        historical_datas = await sync_to_async(list)(
            HistoricalData.objects.filter(fund_id=fund_id)
        )
        if not historical_datas:
            return HistoricalDataCustomResponse(
                status=False,
                message=f"No fund found for fund ID {fund_id}",
                data={},
                status_code=404,
            )
        response_data = HistoricalDataResponseData(
            fund_id=fund_id,
            historical_data=[
                HistoricalDataObject(
                    date=hd.date,
                    open=hd.open,
                    high=hd.high,
                    low=hd.low,
                    close=hd.close,
                    adj_close=hd.adj_close,
                    volume=hd.volume,
                )
                for hd in historical_datas
            ],
        ).model_dump()

        return HistoricalDataCustomResponse(
            status=True,
            message=f"Fund with ID {fund_id} found",
            data=response_data,
            status_code=200,
        )
    except Exception as e:
        return HistoricalDataCustomResponse(
            status=False,
            message=f"Error occured while retriving historical data for mutual fund with id {fund_id}, {str(e)}",
            data={},
            status_code=400,
        )
