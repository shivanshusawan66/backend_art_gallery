from app.schemas.v1.forms import FormSchema,Field
from fastapi import APIRouter,Form,Request
import logging
from typing import Optional, List
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


templates = Jinja2Templates(directory="templates")


router=APIRouter()
logger=logging.getLogger(__name__)

form_schema = FormSchema(fields=[
    Field(
        id="shares-holdings",
        name="sharesHoldings",
        label="What is the value of your current holdings in Shares?",
        type="select",
        options=[
            {"value": "first_time", "label": "I am a first-time investor"},
            {"value": "less_than_50000", "label": "Less than INR 50,000"},
            {"value": "50000_to_200000", "label": "INR 50,000 – INR 200,000"},
            {"value": "200000_to_500000", "label": "INR 200,000 – INR 500,000"},
            {"value": "more_than_500000", "label": "More than INR 500,000"}
        ],
        triggers=["change"],
        visibilityDecisions=[
            {
                "value": ["less_than_50000", "50000_to_200000", "200000_to_500000", "more_than_500000"],
                "show": ["shares-check-portfolio", "shares-rebalance"]
            },
            {
                "value": ["first_time"],
                "hide": ["shares-check-portfolio", "shares-rebalance"]
            }
        ]
    ),
    Field(
        id="shares-check-portfolio",
        name="sharesCheckPortfolio",
        label="How often do you check your Shares portfolio?",
        type="select",
        options=[
            {"value": "daily", "label": "Daily"},
            {"value": "weekly", "label": "Once every week"},
            {"value": "monthly", "label": "Once every month"},
            {"value": "quarterly", "label": "Once every quarter"},
            {"value": "six_months", "label": "Once every six months"}
        ],
        hidden=True
    ),
    Field(
        id="shares-rebalance",
        name="sharesRebalance",
        label="How often do you rebalance your Shares portfolio?",
        type="select",
        hidden=True,
        options=[
            {"value": "monthly", "label": "Once every month"},
            {"value": "quarterly", "label": "Once every quarter"},
            {"value": "six_months", "label": "Once every six months"},
            {"value": "yearly", "label": "Once every year"},
            {"value": "never", "label": "I don’t rebalance"}
        ]
    ),
    Field(
        id="mutual-funds-holdings",
        name="mutualFundsHoldings",
        label="What is the value of your current holdings in Mutual Funds?",
        type="select",
        options=[
            {"value": "first_time", "label": "I am a first-time investor"},
            {"value": "less_than_50000", "label": "Less than INR 50,000"},
            {"value": "50000_to_200000", "label": "INR 50,000 – INR 200,000"},
            {"value": "200000_to_500000", "label": "INR 200,000 – INR 500,000"},
            {"value": "more_than_500000", "label": "More than INR 500,000"}
        ],
        triggers=["change"],
        visibilityDecisions=[
            {
                "value": ["less_than_50000", "50000_to_200000", "200000_to_500000", "more_than_500000"],
                "show": ["sip-count", "sip-frequency", "mf-check-portfolio", "mf-rebalance"]
            },
            {
                "value": ["first_time"],
                "hide": ["sip-count", "sip-frequency", "mf-check-portfolio", "mf-rebalance"]
            }
        ]
    ),
    Field(
        id="sip-count",
        name="sipCount",
        label="How many active SIP investments are you doing currently?",
        type="select",
        hidden=True,
        options=[
            {"value": "1_3", "label": "1-3"},
            {"value": "4_7", "label": "4-7"},
            {"value": "7_10", "label": "7 - 10"},
            {"value": "more_than_10", "label": "More than 10"}
        ]
    ),
    Field(
        id="sip-frequency",
        name="sipFrequency",
        label="What is the average frequency of your SIPs?",
        type="select",
        hidden=True,
        options=[
            {"value": "weekly", "label": "Weekly"},
            {"value": "fortnightly", "label": "Fortnightly"},
            {"value": "monthly", "label": "Monthly"},
            {"value": "quarterly", "label": "Quarterly"}
        ]
    ),
    Field(
        id="mf-check-portfolio",
        name="mfCheckPortfolio",
        label="How often do you check your Mutual Funds portfolio?",
        type="select",
        hidden=True,
        options=[
            {"value": "weekly", "label": "Once every week"},
            {"value": "monthly", "label": "Once every month"},
            {"value": "quarterly", "label": "Once every quarter"},
            {"value": "six_months", "label": "Once every six months"},
            {"value": "yearly", "label": "Once every year"}
        ]
    ),
    Field(
        id="mf-rebalance",
        name="mfRebalance",
        label="How often do you rebalance your Mutual Funds portfolio?",
        type="select",
        hidden=True,
        options=[
            {"value": "six_months", "label": "Once every six months"},
            {"value": "yearly", "label": "Once every year"},
            {"value": "two_years", "label": "Once every two years"},
            {"value": "never", "label": "I don’t rebalance"}
        ]
    ),
    Field(
        id="both-investments",
        name="bothInvestments",
        label="How often do you look at past performance when selecting an investment?",
        type="select",
        visibilityDecisions=[
            {
                "value": ["less_than_50000", "50000_to_200000", "200000_to_500000", "more_than_500000"],
                "show": ["past-performance", "sunk-cost-bias", "market-volatility", "check-during-downturns"]
            }
        ],
        options=[
            {"value": "always", "label": "Always, it’s my main criterion"},
            {"value": "sometimes", "label": "Sometimes, but I consider other factors too"},
            {"value": "rarely", "label": "Rarely, I focus on future potential"}
        ]
    ),
    Field(
        id="sunk-cost-bias",
        name="sunkCostBias",
        label="Do you find it hard to sell an underperforming investment because of the time and money already invested (sunk cost bias)?",
        type="select",
        hidden=True,
        options=[
            {"value": "yes", "label": "Yes, I often hold onto investments longer than I should"},
            {"value": "sometimes", "label": "Sometimes, but I try to be rational about it"},
            {"value": "no", "label": "No, I sell if it doesn’t meet my expectations"}
        ]
    ),
    Field(
        id="market-volatility",
        name="marketVolatility",
        label="How do you react when the stock market becomes volatile?",
        type="select",
        hidden=True,
        options=[
            {"value": "anxious", "label": "I become anxious and consider selling my investments"},
            {"value": "calm", "label": "I remain calm but monitor my portfolio more closely"},
            {"value": "unconcerned", "label": "I am not concerned about short-term volatility"}
        ]
    ),
    Field(
        id="check-during-downturns",
        name="checkDuringDownturns",
        label="Do you find yourself frequently checking your investments during market downturns?",
        type="select",
        hidden=True,
        options=[
            {"value": "multiple_times", "label": "Yes, I check multiple times a day"},
            {"value": "occasionally", "label": "Occasionally, when I see a significant drop"},
            {"value": "long_term", "label": "No, I stick to my long-term strategy"}
        ]
    ),
])

@router.get("/example_form", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("example_form.html", {"request": request})

@router.get("/form-schema")
async def get_form_schema():
    """
    Endpoint to get the form schema.
    """
    print("Form schema requested")
    print([field.dict() for field in form_schema.fields])
    return form_schema

@router.post("/submit-form")
async def submit_form(
    shares_holdings: str = Form(...),
    shares_check_portfolio: Optional[str] = Form(None),
    shares_rebalance: Optional[str] = Form(None),
    mutual_funds_holdings: Optional[str] = Form(None),
    sip_count: Optional[str] = Form(None),
    sip_frequency: Optional[str] = Form(None),
    mf_check_portfolio: Optional[str] = Form(None),
    mf_rebalance: Optional[str] = Form(None),
    both_investments: Optional[str] = Form(None),
    sunk_cost_bias: Optional[str] = Form(None),
    market_volatility: Optional[str] = Form(None),
    check_during_downturns: Optional[str] = Form(None)
):
    """
    This endpoint processes the submitted form data.
    """
    form_data = {
        "shares_holdings": shares_holdings,
        "shares_check_portfolio": shares_check_portfolio,
        "shares_rebalance": shares_rebalance,
        "mutual_funds_holdings": mutual_funds_holdings,
        "sip_count": sip_count,
        "sip_frequency": sip_frequency,
        "mf_check_portfolio": mf_check_portfolio,
        "mf_rebalance": mf_rebalance,
        "both_investments": both_investments,
        "sunk_cost_bias": sunk_cost_bias,
        "market_volatility": market_volatility,
        "check_during_downturns": check_during_downturns
    }

    return {"message": "Form submitted successfully", "data": form_data}