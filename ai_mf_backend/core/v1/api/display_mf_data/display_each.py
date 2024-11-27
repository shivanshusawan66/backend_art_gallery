from fastapi import APIRouter
from asgiref.sync import sync_to_async

from ai_mf_backend.models.v1.database.mutual_fund import (
    AnnualReturn,
    PerformanceData,
    RiskStatistics,
    TrailingReturn,
    HistoricalData,
)


router = APIRouter()


@router.get("api/v1/fund_annual_return/{id}")
async def get_annual_returns(fund_id: int):
    annual_returns = await sync_to_async(list)(
        AnnualReturn.objects.filter(fund_id=fund_id)
    )

    return {
        "fund_id": fund_id,
        "annual_returns": [
            {
                "year": ar.year,
                "fund_return": ar.fund_return,
            }
            for ar in annual_returns
        ],
    }


@router.get("api/v1/fund_risk_statistics/{id}")
async def get_risk_statistics(fund_id: int):
    risk_statistics = await sync_to_async(list)(
        RiskStatistics.objects.filter(fund_id=fund_id)
    )
    return {
        "fund_id": fund_id,
        "risk_statistics": [
            {
                "period": rs.period,
                "alpha": rs.alpha,
                "beta": rs.beta,
                "mean_annual_return": rs.mean_annual_return,
                "r_squared": rs.r_squared,
                "standard_deviation": rs.standard_deviation,
                "sharpe_ratio": rs.sharpe_ratio,
                "treynor_ratio": rs.treynor_ratio,
            }
            for rs in risk_statistics
        ],
    }


@router.get("api/v1/fund_performance/{id}")
async def get_performance(fund_id: int):

    performance = await sync_to_async(
        lambda: PerformanceData.objects.get(fund_id=fund_id)
    )()
    return {
        "fund_id": fund_id,
        "ytd_return": performance.ytd_return,
        "average_return_5y": performance.average_return_5y,
        "number_of_years_up": performance.number_of_years_up,
        "number_of_years_down": performance.number_of_years_down,
        "best_1y_total_return": performance.best_1y_total_return,
        "worst_1y_total_return": performance.worst_1y_total_return,
        "best_3y_total_return": performance.best_3y_total_return,
        "worst_3y_total_return": performance.worst_3y_total_return,
    }


@router.get("api/v1/fund_trailing_return/{id}")
async def get_trailing_return(fund_id: int):
    trailing_return = await sync_to_async(list)(
        TrailingReturn.objects.filter(fund_id=fund_id)
    )
    return {
        "fund_id": fund_id,
        "performance": [
            {
                "metric": tr.metric,
                "fund_return": tr.fund_return,
                "benchmark_return": tr.benchmark_return,
            }
            for tr in trailing_return
        ],
    }


@router.get("api/v1/fund_historical_data/{id}")
async def get_historical_data(fund_id: int):
    historical_data = await sync_to_async(list)(
        HistoricalData.objects.filter(fund_id=fund_id)
    )
    return {
        "fund_id": fund_id,
        "historical_data": [
            {
                "date": hd.date,
                "open": hd.open,
                "high": hd.high,
                "low": hd.low,
                "close": hd.close,
                "adj_close": hd.adj_close,
                "volume": hd.volume,
            }
            for hd in historical_data
        ],
    }
