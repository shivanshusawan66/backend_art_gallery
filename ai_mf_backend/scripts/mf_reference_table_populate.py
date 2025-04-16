import os
import sys
import django
import logging
from django.db import connection
from django.db import transaction


sys.path.append(os.getcwd())

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "ai_mf_backend.config.v1.django_settings"
)

django.setup()
logger = logging.getLogger(__name__)

from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *


# Define mapping using string identifiers (enum names)
TABLE_MARKER_MAPPING = {
    MFSchemeMasterInDetails:["status","schemecode"],
    MFSchemeMaster: ["schemecode","scheme_name"],
    MFAMCMaster: ["setup_date"],
    MFSchemeClassMaster: ["asset_type","classcode"],
    MFSchemeAUM:["total"],
    MFCAGRReturn: ["schemecode", "_1yrret", "_3yearret", "_5yearret"],
    MFSchemeRGESS: ["schemename"],
    # "Incept_date","primary_fund","classcode"
    # "TYPE_MST": ["type_code", "type"],
    # "SCHEME_MASTER": ["color"],
    # "MF_RATIOS": ["sd_Y","beta_y","treynor_y","jalpha_y","sortino_y"],
    # "SCHEME_LOAD": ["EXITLOAD"],
    # "MF_PORTFOLIO": ["schemecode","ASECT_CODE", "holdpercentage","rating","invenddate"],
    # "ASECT_MST": ["asect_code", "as_name"],
    # "SCHEME_EQ_DETAILS": ["MCAP"],
    # "COMPANY_MCAP": ["mcap"],
    # "AVG_MATURITY": ["avg mat num", "avg_mat_days"],
    # "EXPENSE_RATIO": ["expratio"],
    # "MF_SIP": ["schemecode"],
    # "MF_RETURN": ["_1yrret", "_3yearet", "_5yearret"],
    # #"MF_Absolute_Return":["5yearret"],
    # #"SCHEME_ISIN_MASTER": ["scheme_code", "isin"],
    # "NAV_HIST": ["navrs"],
    # "CURRENT_NAV": ["navrs"],
    # #"MF_LOAD_TYPE_MASTER":[""]
}

def truncate_table(model):
    table_name = model._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')

def clear_tables():
    """Clear existing data """
    truncate_table(MFReferenceTable)
    print("Reference tables are cleared")

def populate_reference_table():
    """Populate MFReferenceTable using model class names (not DB table names)"""
    try:
        with transaction.atomic():
            for model, fields in TABLE_MARKER_MAPPING.items():
                model_name = model.__name__  
                model_fields = [field.name for field in model._meta.fields]

                for field in fields:
                    if field not in model_fields:
                        logger.warning(f"WARNING: Field '{field}' not found in model '{model_name}'. Skipping...")
                        continue

                    MFReferenceTable.objects.update_or_create(
                        table_name=model_name,  
                        marker_name=field,
                        defaults={
                            "display_name": field.replace("_", " ").title(),
                        }
                    )

        print("MFReferenceTable populated successfully.")
    except Exception as e:
        logger.error(f"Error populating reference table: {str(e)}")

if __name__ == "__main__":
    clear_tables()
    populate_reference_table()