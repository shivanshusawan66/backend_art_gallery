import os
import random
import sys
import django
from django.db import connection
from django.db import transaction

from sklearn.preprocessing import KBinsDiscretizer
import numpy as np
from datetime import datetime



sys.path.append(rf"{os.getcwd()}")

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)

django.setup()


from ai_mf_backend.models.v1.database.mf_embedding_table import *
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *


SECTION_MARKER_MAP = {
    "Experience Level": ["color", "since", "type", "setup_date", "Incept_date"],
    "Risk Tolerance": ["sharpe_y", "sortino_y", "beta_y", "_1yworstret", "EXITLOAD"],
    "Investment Duration": ["avg_mat_num", "tenure_number", "IsRedeemAvailable", "LockIn", "turnover_ratio"],
    "Decision Making Style": ["expratio", "trackingError", "jalpha_y", "fund_mgr1", "sip"],
    "Emotional Reactions to Market Changes": ["_52weekhhigh", "gross", "ytdret", "adjustednav_c", "_3yworstret"],
    "Research and Professional Advice": ["sebi_reg_no", "trustee_name", "cust_name", "IsPurchaseAvailable", "Benchmark_Weightage"],
    "Sectoral and Investment Preferences": ["sect_name", "asect_type", "mcap", "sub_category", "rating"]
}

MARKER_MODEL_MAP = {
    MFAMCMaster: ["setup_date", "trustee_name"],
    MFAssetAllocationMaster: ["asect_type"],
    MFCategoryWiseReturn: ["_1yworstret", "_3yworstret"],
    MFBenchmarkIndicesAbsoluteReturn: ["ytdret"],
    MFCompanyMcap: ["mcap"],
    MFCustodianMaster: ["cust_name"],
    MFDividendDetails: ["gross"],
    MFNetAssetValueHighLow: ["_52weekhhigh",],
    MFNetAssetValueHistorical: ["adjustednav_c"],
    MFPortfolio: ["rating", "sect_name"],
    MFRatios1Year: ["beta_y", "jalpha_y", "sharpe_y", "sortino_y"],
    MFRatiosDefaultBenchmark1Year: ["trackingError"],
    MFRegistrarMaster: ["sebi_reg_no"],
    MFSchemeAverageMaturity: ["avg_mat_num", "turnover_ratio"],
    MFSchemeClassMaster: ["sub_category"],
    MFSchemeEntryExitLoad: ["EXITLOAD"],
    MFSchemeFMPYieldDetails: ["tenure_number"],
    MFSchemeIndexMapping: ["Benchmark_Weightage"],
    MFSchemeMaster: ["color"],
    MFSchemeMasterInDetails: ["Incept_date", "IsPurchaseAvailable", "LockIn", "fund_mgr1", "since"], 
    MFSchemeMonthWiseExpenseRatio: ["expratio"],
    MFSystematicInvestmentPlan: ["sip"],
}


def truncate_table(model):
    table_name = model._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")

def clear_tables():
    """Clear existing data from all relevant tables and reset the auto-increment."""
    truncate_table(MFMarker)
    truncate_table(MFMarkerOptions)
    print("Existing data cleared and auto-increment reset successfully.")


def populate_section_markers():
    data = SECTION_MARKER_MAP

    with transaction.atomic():
        for section_name, markers in data.items():
            try:
                section = Section.objects.get(section=section_name)
            except Section.DoesNotExist:
                print(f"Warning: Section '{section_name}' does not exist. Skipping...")
                continue

            for marker in markers:
                MFMarker.objects.create(
                    section_id=section,
                    marker=marker,
                    initial_marker_weight=round(random.uniform(0, 1), 2)
                )

    print("Section markers populated.")

def populate_marker_options():
    """
    Populate MFMarkerOptions using field data from mapped models based on markers,
    using scikit-learn for numeric binning with proper datetime handling.
    Range data formatted as [start range,end range].
    """
    with transaction.atomic():
        for model, marker_fields in MARKER_MODEL_MAP.items():
            for marker_field in marker_fields:
                try:
                    marker_obj = MFMarker.objects.get(marker=marker_field)
                except MFMarker.DoesNotExist:
                    print(f"Warning: Marker '{marker_field}' not found in MFMarker.")
                    continue

                # Get distinct non-null values from the model's field
                values = (
                    model.objects.values_list(marker_field, flat=True)
                    .distinct()
                    .exclude(**{f"{marker_field}__isnull": True})
                )
                
                values = [v for v in values if v not in ["", None]]

                if not values:
                    continue

                # Take up to 100 random samples to determine data type
                sample_size = min(100, len(values))
                sample_values = random.sample(values, sample_size) if len(values) > 1 else values

                # Determine predominant data type from samples
                datetime_count = sum(1 for v in sample_values if isinstance(v, datetime))
                numeric_count = 0

                for v in sample_values:
                    if isinstance(v, (int, float)):
                        numeric_count += 1
                    elif isinstance(v, str):
                        try:
                            float(v)
                            numeric_count += 1
                        except ValueError:
                            pass
                
                # Case 1: Datetime values - convert to timestamps for scikit-learn
                if datetime_count >= sample_size / 2:
                # Convert datetimes to age (or years since date)
                    now = datetime.now()
                    ages = []
                    for v in values:
                        if isinstance(v, datetime):
                            age = now.year - v.year
                            ages.append(age)

                    # Use unique, sorted ages
                    unique_ages = sorted(set(ages))
                    for position, age in enumerate(unique_ages, start=1):
                        MFMarkerOptions.objects.create(
                            section_id=marker_obj.section_id,
                            marker_id=marker_obj,
                            option=str(age),
                            position=position,
                            option_weight=round(random.uniform(0, 1), 2)
                        )
                
                # Case 2: Try to handle as numeric values
                else:
                    # Try to convert all values to numeric
                    try:
                        # Handle different numeric formats
                        numeric_values = []
                        for v in values:
                            if isinstance(v, (int, float)):
                                numeric_values.append(float(v))
                            elif isinstance(v, str):
                                try:
                                    numeric_values.append(float(v))
                                except ValueError:
                                    raise ValueError("Non-numeric value found")
                            else:
                                raise ValueError("Non-numeric value found")
                        
                        numeric_array = np.array(numeric_values).reshape(-1, 1)
                        
                        # Now process numeric values with scikit-learn
                        if len(numeric_values) > 5 and np.max(numeric_array) > np.min(numeric_array):
                            # Use scikit-learn for numeric binning
                            discretizer = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='uniform')
                            discretizer.fit(numeric_array)
                            
                            bin_edges = discretizer.bin_edges_[0]
                            
                            for i in range(5):
                                bin_start = bin_edges[i]
                                bin_end = bin_edges[i+1]
                                
                                # Format in requested format [start,end]
                                option_label = f"[{bin_start:.2f},{bin_end:.2f}]"
                                
                                MFMarkerOptions.objects.create(
                                    section_id=marker_obj.section_id,
                                    marker_id=marker_obj,
                                    option=option_label,
                                    position=i+1,
                                    option_weight=round(random.uniform(0, 1), 2)
                                )
                        else:
                            # If all values are similar or few in number
                            sorted_values = sorted(numeric_values)
                            for position, value in enumerate(sorted_values, start=1):
                                MFMarkerOptions.objects.create(
                                    section_id=marker_obj.section_id,
                                    marker_id=marker_obj,
                                    option=str(value),
                                    position=position,
                                    option_weight=round(random.uniform(0, 1), 2)
                                )
                    
                    except ValueError:
                        # Case 3: Text values (when numeric conversion fails)
                        sorted_values = sorted(str(v) for v in values)
                        for position, value in enumerate(sorted_values, start=1):
                            MFMarkerOptions.objects.create(
                                section_id=marker_obj.section_id,
                                marker_id=marker_obj,
                                option=str(value),
                                position=position,
                                option_weight=round(random.uniform(0, 1), 2)
                            )

    print("MFMarkerOptions populated with scikit-learn binning and [start,end] range format.")

def populate_all():
    populate_section_markers()
    populate_marker_options()

if __name__ == '__main__':
    clear_tables()  
    populate_all()