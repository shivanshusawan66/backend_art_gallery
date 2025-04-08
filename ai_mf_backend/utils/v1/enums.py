from enum import Enum
from datetime import datetime
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *
from ai_mf_backend.config.v1.api_config import api_config

class APIConstants(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class SignUpType(Enum):
    otp = "otp"
    password = "password"


class ReferenceTableEnums(Enum):
    projection_table_mapping = "projection_table_mapping"


date_str = datetime.today().strftime("%d%m%Y")


class FetchApiConfig(Enum):
    DATA1 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Amc_mst_new",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFTypeMaster,
        1000,
    )
    DATA2=(
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Amc_keypersons",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFAMCKeyPerson,
        1000,

    )
    DATA3=(
          "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_master",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeMaster,
        1000,
    )
    DATA4=(
         "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_details",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeMasterInDetails,
        1000,
    )
    DATA5=(
         "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_rtcode",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeRTCode,
        1000,
    )
    DATA6=(
         "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "schemeisinmaster",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeIsInMaster,
        1000,
    )
    DATA7=(
         "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Type_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFTypeMaster,
        1000,
    )
    DATA8=(
         "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Option_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFOptionMaster,
        1000,
    )
    DATA9=(
         "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Sclass_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeClassMaster,
        1000,
    )
    DATA10=(
         "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Rt_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFRegistrarMaster,
        1000,
    )
    DATA11=(
         "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Plan_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFPlanMaster,
        1000,
    )
    DATA12=(
         "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Cust_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFCustodianMaster,
        1000,
    )
    DATA13 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Fundmanager_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFFundManagerMaster,
        1000,
    )
    DATA14 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Div_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFDividendMaster,
        1000,
    )
    DATA15 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_objective",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeObjective,
        1000,
    )
    DATA16 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mf_sip",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSystematicInvestmentPlan,
        1000,
    )
    DATA17 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mf_swp",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSystematicWithdrawalPlan,
        1000,
    )
    DATA18 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mf_stp",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSystematicTransferPlan,
        1000,
    )
    DATA19 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_index_part",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeIndexMapping,
        1000,
    )
    DATA20 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Index_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFIndexMaster,
        1000,
    )
    DATA21 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Schemeload",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeEntryExitLoad,
        1000,
    )
    DATA22 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Loadtype_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFLoadTypeMaster,
        1000,
    )
    DATA23 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Companymaster",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFCompanyMaster,
        1000,
    )
    DATA24 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Industry_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFIndustryMaster,
        1000,
    )
    DATA25 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Asect_mst",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFAssetAllocationMaster,
        1000,
    )
    DATA26 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_rgess",
            "date": date_str,
            "section": "MFMaster",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeRGESS,
        1000,
    )
    
    DATA27 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mf_portfolio",
            "date": date_str,
            "section": "MFPortfolio",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFPortfolio,
        1000,
    )
    DATA28 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Amc_paum",
            "date": date_str,
            "section": "MFPortfolio",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFAMCPortfolioAUM,
        1000,
    )
    DATA29 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_paum",
            "date": date_str,
            "section": "MFPortfolio",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemePortfolioAUM,
        1000,
    )
    DATA30 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "amc_aum",
            "date": date_str,
            "section": "MFPortfolio",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFAMCAUM,
        1000,
    )
    DATA31 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "scheme_aum",
            "date": date_str,
            "section": "MFPortfolio",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeAUM,
        1000,
    )
    DATA32 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Portfolio_inout",
            "date": date_str,
            "section": "MFPortfolio",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFPortfolioInOut,
        1000,
    )
    DATA33 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Avg_scheme_aum",
            "date": date_str,
            "section": "MFPortfolio",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFAverageSchemeAUM,
        1000,
    )
    DATA34 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Currentnav",
            "date": date_str,
            "section": "MFNAV",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFNSEAssetValueLatest,
        1000,
    )
    DATA35 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Navhist",
            "date": date_str,
            "section": "MFNAV",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFNetAssetValueHistorical,
        1000,
    )
    DATA36 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Navhist_HL",
            "date": date_str,
            "section": "MFNAV",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFNetAssetValueHighLow,
        1000,
    )
    DATA37 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mf_return",
            "date": date_str,
            "section": "MFReturn",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFReturn,
        1000,
    )
    DATA38 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mf_abs_return",
            "date": date_str,
            "section": "MFReturn",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFAbsoluteReturn,
        1000,
    )
    DATA39 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mf_ans_return",
            "date": date_str,
            "section": "MFReturn",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFAnnualizedReturn,
        1000,
    )
    DATA40 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mf_cagr_return",
            "date": date_str,
            "section": "MFReturn",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFCAGRReturn,
        1000,
    )
    DATA41 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "ClassWiseReturn",
            "date": date_str,
            "section": "MFReturn",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFCategoryWiseReturn,
        1000,
    )
    DATA42 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "BM_AbsoluteReturn",
            "date": date_str,
            "section": "MFReturn",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFBenchmarkIndicesAbsoluteReturn,
        1000,
    )
    DATA43 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "BM_AnnualisedReturn",
            "date": date_str,
            "section": "MFReturn",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFBenchmarkIndicesAnnualisedReturn,
        1000,
    )
    DATA44 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mf_ratio",
            "date": date_str,
            "section": "MFRatios",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFRatios1Year,
        1000,
    )
    DATA45 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "MF_Ratios_DefaultBM",
            "date": date_str,
            "section": "MFRatios",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFRatiosDefaultBenchmark1Year,
        1000,
    )
    DATA46 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Ratio_3Year_MonthlyRet",
            "date": date_str,
            "section": "MFRatios",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFRatios3Year,
        1000,
    )
    DATA47 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Divdetails",
            "date": date_str,
            "section": "MFDividend",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFDividendDetails,
        1000,
    )
    DATA48 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Expenceratio",
            "date": date_str,
            "section": "MFExpense",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeMonthWiseExpenseRatio,
        1000,
    )
    DATA49 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_eq_details",
            "date": date_str,
            "section": "MFEquityDetails",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeEquityDetails,
        1000,
    )
    DATA50 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "fmp_yielddetails",
            "date": date_str,
            "section": "MFYield",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeFMPYieldDetails,
        1000,
    )
    DATA51 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Avg_maturity",
            "date": date_str,
            "section": "MFMaturity",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeAverageMaturity,
        1000,
    )
    DATA52 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Fvchange",
            "date": date_str,
            "section": "MFFaceValue",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFFaceValueChange,
        1000,
    )
    DATA53 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_Name_Change",
            "date": date_str,
            "section": "MFNameChange",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeNameChange,
        1000,
    )
    DATA54 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "DailyFundmanager",
            "date": date_str,
            "section": "MFFundManager",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFFundmanager,
        1000,
    )
    DATA55 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Mergedschemes",
            "date": date_str,
            "section": "MFMerged",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFMergedschemes,
        1000,
    )
    DATA56 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "MFBULKDEALS",
            "date": date_str,
            "section": "MFBulkDeals",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFBulkDeals,
        1000,
    )
    DATA57 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "Scheme_assetalloc",
            "date": date_str,
            "section": "MFAssetAllocation",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFSchemeAssetAllocation,
        1000,
    )
    DATA58 = (
        "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?",
        {
            "filename": "CompanyMcap",
            "date": date_str,
            "section": "MFCompanyMcap",
            "sub": "",
            "token": api_config.FETCH_DATA_API_TOKEN,
        },
        MFCompanyMcap,
        1000,
    )
    
    

    @property
    def url(self):
        return self.value[0]

    @property
    def params(self):
        return self.value[1]

    @property
    def model(self):
        return self.value[2]

    @property
    def batch_size(self):
        return self.value[3]
