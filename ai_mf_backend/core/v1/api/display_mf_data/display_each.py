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

@router.get('api/v1/fund_annual_return/{id}')

async def get_annual_returns( fund_id : int):
    annual_returns = await sync_to_async(list)(
        AnnualReturn.objects.filter(fund_id=fund_id)
    )
    

    return {
        "fund_id" : fund_id, 
        "annual_returns": [
            {
                "year": ar.year,
                "fund_return": ar.fund_return,
                
            }
            for ar in annual_returns
        ],
        
    }


@router.get('api/v1/fund_performance/{id}')

async def get_performance( fund_id : int):
    performance = await sync_to_async( PerformanceData.objects.filter(fund_id=fund_id).first)()
    return {
        "fund_id" : fund_id, 
        "performance" : performance
    }


@router.get('api/v1/fund_risk_statistics/{id}')

async def get_risk_statistics( fund_id : int):
    
    risk_statistics = await sync_to_async( RiskStatistics.objects.filter(fund_id=fund_id).first)()
    return {
        "fund_id" : fund_id, 
        "risk_statistics" : risk_statistics
    }


@router.get('api/v1/fund_trailing_return/{id}')

async def get_trailing_return( fund_id : int):
    trailing_return =  await sync_to_async(TrailingReturn.objects.filter(fund_id=fund_id).first)()
    return {
        "fund_id" : fund_id, 
        "trailing_return" : trailing_return
    }

@router.get('api/v1/fund_historical_data/{id}')

async def get_historical_data( fund_id : int):
    historical_data =  await sync_to_async(HistoricalData.objects.filter(fund_id=fund_id).first)()
    return {
        "fund_id" : fund_id, 
        "historical_data" : historical_data
    }