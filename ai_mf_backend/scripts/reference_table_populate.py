import os
import sys
import django
import logging
from datetime import datetime
from django.db import transaction

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings")
logger = logging.getLogger(__name__)

# Define mapping using string identifiers (enum names)
projection_table_mapping = {
    "SCHEME_DETAILS": ["type_code","Incept_date","primary_fund","classcode"],
    "SCHEME_PAUM": ["aum"],
    "TYPE_MST": ["type_code", "type"],
    "SCHEME_MASTER": ["color"],
    "MF_RATIOS": ["sd_Y","beta_y","treynor_y","jalpha_y","sortino_y"],
    "SCHEME_LOAD": ["EXITLOAD"],
    "MF_PORTFOLIO": ["schemecode","ASECT_CODE", "holdpercentage","rating","invenddate"],
    "ASECT_MST": ["asect_code", "as_name"],
    "SCLASS_MST": ["classcode", "classname"],
    "SCHEME_EQ_DETAILS": ["MCAP"],
    "COMPANY_MCAP": ["mcap"],
    "AVG_MATURITY": ["avg mat num", "avg_mat_days"],
    "EXPENSE_RATIO": ["expratio"],
    "MF_SIP": ["schemecode"],
    "MF_RETURN": ["1yrret", "3yearet", "5yearret"],
    #"MF_Absolute_Return":["5yearret"],
    "MF_CAGR_RETURN": ["schemecode", "1yrret", "3yearret", "5yearret"],
    #"SCHEME_ISIN_MASTER": ["scheme_code", "isin"],
    "NAV_HIST": ["navrs"],
    "CURRENT_NAV": ["navrs"],
    #"MF_LOAD_TYPE_MASTER":[""]
}

def clear_tables():
    """Clear existing data from all relevant tables."""
    from ai_mf_backend.models.v1.database.reference_table import Reference
    Reference.objects.all().delete()
    logger.info("Existing data cleared successfully.")

def get_enum_mapping():
    """Convert string-based mapping to actual enums after Django setup"""
    from ai_mf_backend.utils.v1.enums import ReferenceTableEnums
    return {
        getattr(ReferenceTableEnums, key): value
        for key, value in projection_table_mapping.items()
    }

def populate_data():
    """
    Populates the Reference table with initial projection mappings.
    Run once during setup or when schema changes.
    """
    from ai_mf_backend.models.v1.database.reference_table import Reference
    
    enum_mapping = get_enum_mapping()
    
    with transaction.atomic():
        for table_enum, columns in enum_mapping.items():
            for column in columns:
                Reference.objects.update_or_create(
                    table_name=table_enum.value,
                    column_name=column,
                    defaults={
                        "display_name": column.replace('_', ' ').title(),
                        "update_date": datetime.utcnow()
                    }
                )

if __name__ == "__main__":
    django.setup()
    populate_data()