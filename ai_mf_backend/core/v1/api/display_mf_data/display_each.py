from fastapi import APIRouter, Depends
from asgiref.sync import sync_to_async


from ai_mf_backend.config.v1.api_config import api_config
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
    CustomMutualFundOverviewResponseData,
    CustomMutualFundOverviewCustomResponse,
    PerformanceDataResponseData,
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


from ai_mf_backend.utils.v1.validators.input import validate_fund_id


router = APIRouter()

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_overview/{fund_id}")
async def get_overview(fund_id: int = Depends(validate_fund_id)):

    
    try:

        fund_overview = await sync_to_async(
            MutualFund.objects.only(
                "id", "scheme_name", "q_param", "net_asset_value", "symbol"
            ).get
        )(id=fund_id)

        response_data = CustomMutualFundOverviewResponseData(
            fund_id=fund_id,
            name=fund_overview.scheme_name,
            q_param=fund_overview.q_param,
            nav=fund_overview.net_asset_value,
            symbol=fund_overview.symbol,
        ).model_dump()

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

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_performance/{fund_id}")
async def get_performance(fund_id: int = Depends(validate_fund_id)):
    try:
        performance = await sync_to_async(
            PerformanceData.objects.only(
                "fund_id",
                "ytd_return",
                "average_return_5y",
                "number_of_years_up",
                "number_of_years_down",
                "best_1y_total_return",
                "worst_1y_total_return",
                "best_3y_total_return",
                "worst_3y_total_return",
            ).get
        )(fund_id=fund_id)

        response_data = PerformanceDataResponseData(
            fund_id=fund_id,
            ytd_return=performance.ytd_return,
            average_return_5y=performance.average_return_5y,
            number_of_years_up=performance.number_of_years_up,
            number_of_years_down=performance.number_of_years_down,
            best_1y_total_return=performance.best_1y_total_return,
            worst_1y_total_return=performance.worst_1y_total_return,
            best_3y_total_return=performance.best_3y_total_return,
            worst_3y_total_return=performance.worst_3y_total_return,
        ).model_dump()

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

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_annual_return/{fund_id}")
async def get_annual_returns(fund_id: int = Depends(validate_fund_id)):

    annual_returns = await sync_to_async(list)(
        AnnualReturn.objects.filter(fund_id=fund_id)
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

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_risk_statistics/{fund_id}")
async def get_risk_statistics(fund_id: int = Depends(validate_fund_id)):
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

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_trailing_return/{fund_id}")
async def get_trailing_return(fund_id: int = Depends(validate_fund_id)):
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

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/fund_historical_data/{fund_id}")
async def get_historical_data(fund_id: int = Depends(validate_fund_id)):
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
