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
    MFSchemeMasterInDetails:["status","schemecode","sip","s_name"],
    MFAMCMaster: ["setup_date"],
    MFSchemeClassMaster: ["asset_type","classcode", "category"],
    MFSchemeAUM:["total"],
    MFCAGRReturn: ["_1yrret", "_3yearret", "_5yearret"],
    MFSchemeRGESS: ["schemename"],
    MFRatios1Year: ["sd_y","beta_y","treynor_y","jalpha_y","sortino_y","sharpe_y"],
    MFPortfolio: ["compname", "sect_name", "holdpercentage","fincode"],
    MFCompanyMcap:[ "mode"],
    MFNSEAssetValueLatest:["navrs_current"],
    MFNetAssetValueHistorical:["navrs_historical"],
    MFFundManagerMaster: ["initial", "fundmanager", "qualification", "basicdetails", "experience", "designation", "age"],
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
                for field in fields:

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