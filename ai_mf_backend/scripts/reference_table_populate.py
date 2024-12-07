import os
import django
import logging
from datetime import datetime
from django.db import transaction

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)  # Use your project’s settings path

# Set up Django after setting environment variables
django.setup()

logger = logging.getLogger(__name__)

from ai_mf_backend.models.v1.database.reference_table import Reference

from ai_mf_backend.utils.v1.enums import ReferenceTableEnums


# Clear existing data
def clear_tables():
    """Clear existing data from all relevant tables."""
    Reference.objects.all().delete()
    logger.info("Existing data cleared successfully.")


field_mapping = [
    {
        "table_name": "MutualFund",
        "column_name": "scheme_name",
        "display_name": "scheme_name",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "MutualFund",
        "column_name": "id",
        "display_name": "fund_id",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "MutualFund",
        "column_name": "net_asset_value",
        "display_name": "net_asset_value",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "overview",
        "column_name": "ytd_return",
        "display_name": "ytd_return",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "overview",
        "column_name": "morningstar_rating",
        "display_name": "morningstar_rating",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "overview",
        "column_name": "fund_family",
        "display_name": "fund_family",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "overview",
        "column_name": "net_assets",
        "display_name": "net_assets",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "overview",
        "column_name": "yield_value",
        "display_name": "yield_value",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "overview",
        "column_name": "inception_date",
        "display_name": "inception_date",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "fund_data",
        "column_name": "min_initial_investment",
        "display_name": "min_investment",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "performance_data",
        "column_name": "ytd_return",
        "display_name": "performance_ytd_return",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "performance_data",
        "column_name": "average_return_5y",
        "display_name": "performance_average_return_5y",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "performance_data",
        "column_name": "number_of_years_up",
        "display_name": "number_of_years_up",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "performance_data",
        "column_name": "number_of_years_down",
        "display_name": "number_of_years_down",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "performance_data",
        "column_name": "best_3y_total_return",
        "display_name": "best_3y_total_return",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "performance_data",
        "column_name": "worst_3y_total_return",
        "display_name": "worst_3y_total_return",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "risk_statistics",
        "column_name": "alpha",
        "display_name": "alpha",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "risk_statistics",
        "column_name": "beta",
        "display_name": "beta",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "risk_statistics",
        "column_name": "mean_annual_return",
        "display_name": "mean_annual_return",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "risk_statistics",
        "column_name": "r_squared",
        "display_name": "r_squared",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "risk_statistics",
        "column_name": "standard_deviation",
        "display_name": "standard_deviation",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "risk_statistics",
        "column_name": "sharpe_ratio",
        "display_name": "sharpe_ratio",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
    {
        "table_name": "risk_statistics",
        "column_name": "treynor_ratio",
        "display_name": "treynor_ratio",
        "reference_type": ReferenceTableEnums.projection_table_mapping.value,
    },
]


def populate_data():
    with transaction.atomic():
        for mapping_document in field_mapping:
            mapping_document["add_date"] = datetime.utcnow()
            mapping_document["update_date"] = datetime.utcnow()

            Reference.objects.create(**mapping_document)


if __name__ == "__main__":
    populate_data()
