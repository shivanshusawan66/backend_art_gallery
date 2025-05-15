import os
import sys
import django
import logging

from django.db import connection
from django.db import transaction


sys.path.append(os.getcwd())

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)

django.setup()
logger = logging.getLogger(__name__)

from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *


TABLE_MARKER_MAPPING = {
    'status': (MFSchemeMasterInDetails,),
    'schemecode': (MFSchemeMasterInDetails,),
    'sip': (MFSchemeMasterInDetails,),
    's_name': (MFSchemeMasterInDetails,),
    'setup_date': (MFAMCMaster, "amc_code", "amc_code"),
    'asset_type': (MFSchemeClassMaster, "classcode", "classcode"),
    'classcode': (MFSchemeClassMaster,),
    'category': (MFSchemeClassMaster,),
    'LongSchemeDescrip': (MFSchemeIsInMaster,),
    'ShortSchemeDescrip': (MFSchemeIsInMaster,),
    'total': (MFSchemeAUM,),
    '_1yrret': (MFCAGRReturn,),
    '_3yearret': (MFCAGRReturn,),
    '_5yearret': (MFCAGRReturn,),
    'schemename': (MFSchemeRGESS,),
    'sd_y': (MFRatios1Year,),
    'beta_y': (MFRatios1Year, "schemecode", "schemecode"),
    'treynor_y': (MFRatios1Year,),
    'jalpha_y': (MFRatios1Year, "schemecode", "schemecode"),
    'sortino_y': (MFRatios1Year, "schemecode", "schemecode"),
    'sharpe_y': (MFRatios1Year, "schemecode", "schemecode"),
    'compname': (MFPortfolio,),
    'sect_name': (MFPortfolio,),
    'holdpercentage': (MFPortfolio,),
    'fincode': (MFPortfolio,),
    'mode': (MFCompanyMcap,),
    'navrs': (MFNSEAssetValueLatest,),
    'navrs_current': (MFNSEAssetValueLatest,),
    'navrs_historical': (MFNetAssetValueHistorical,),
    'initial': (MFFundManagerMaster,),
    'fundmanager': (MFFundManagerMaster,),
    'qualification': (MFFundManagerMaster,),
    'basicdetails': (MFFundManagerMaster,),
    'experience': (MFFundManagerMaster,),
    'designation': (MFFundManagerMaster,),
    'age': (MFFundManagerMaster,),
    '_1yrret_absolute': (MFAbsoluteReturn,),
    '_3yearret_absolute': (MFAbsoluteReturn,),
    '_5yearret_absolute': (MFAbsoluteReturn,),
    '_1yrret_annualised': (MFAnnualizedReturn,),
    '_3yearret_annualised': (MFAnnualizedReturn,),
    '_5yearret_annualised': (MFAnnualizedReturn,),
    'frequency': (MFSystematicInvestmentPlan,),
    'expratio': (MFSchemeMonthWiseExpenseRatio, "schemecode", "schemecode"),
    'color': (MFSchemeMaster,"schemecode","schemecode"),
    'type': (MFTypeMaster,"type_code","type_code"),
    '_1yworstret': (MFCategoryWiseReturn,"classcode","classcode"),
    'EXITLOAD': (MFSchemeEntryExitLoad,"schemecode","SCHEMECODE"),
    'avg_mat_num': (MFSchemeAverageMaturity,"schemecode","schemecode"),
    'tenure_number': (MFSchemeFMPYieldDetails,"schemecode","schemecode"),
    'turnover_ratio': (MFSchemeAverageMaturity,"schemecode","schemecode"),
    'trackingError': (MFRatiosDefaultBenchmark1Year,"schemecode","schemecode"),
    '_52weekhhigh': (MFNetAssetValueHighLow,"schemecode","schemecode"),
    'gross': (MFDividendDetails,"schemecode","schemecode"),
    'ytdret': (MFCategoryWiseReturn,"classcode","classcode"),
    'adjustednav_c': (MFNetAssetValueHistorical,"schemecode","schemecode"),
    '_3yworstret': (MFCategoryWiseReturn,"classcode","classcode"),
    'sebi_reg_no': (MFRegistrarMaster,"rt_code","rt_code"),
    'trustee_name': (MFAMCMaster,"amc_code","amc_code"),
    'cust_name': (MFCustodianMaster,"cust_code","cust_code"),
    'Benchmark_Weightage': (MFSchemeIndexMapping,"schemecode","SCHEMECODE"),
    'MCAP': (MFSchemeEquityDetails,"schemecode","SchemeCode"),
    'sub_category': (MFSchemeClassMaster,"classcode","classcode")
}


def truncate_table(model):
    table_name = model._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')


def clear_tables():
    """Clear existing data"""
    truncate_table(MFReferenceTable)
    print("Reference tables are cleared")


def populate_reference_table():
    """Populate MFReferenceTable using field-to-model mapping and optional reference fields."""
    try:
        with transaction.atomic():
            for marker_name, mapping in TABLE_MARKER_MAPPING.items():
                model_class = mapping[0]
                lookup_field = mapping[2] if len(mapping) > 2 else None
                outer_ref = mapping[1] if len(mapping) > 1 else None

                model_name = model_class.__name__

                MFReferenceTable.objects.update_or_create(
                    table_name=model_name,
                    marker_name=marker_name,
                    defaults={
                        "display_name": marker_name.replace("_", " ").title(),
                        "lookup_field": lookup_field,
                        "outer_ref": outer_ref,
                    },
                )

        logger.info("MFReferenceTable populated successfully.")
    except Exception as e:
        logger.error(f"Error populating reference table: {str(e)}")

if __name__ == "__main__":
    clear_tables()
    populate_reference_table()