import os
import random
import sys
import warnings
import numpy as np
import django
from datetime import datetime, date
from django.db import connection
from django.db import transaction
from django.utils import timezone
from django.db.models import OuterRef, Subquery, F
from sklearn.preprocessing import KBinsDiscretizer


sys.path.append(rf"{os.getcwd()}")

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)

django.setup()


from ai_mf_backend.models.v1.database.mf_embedding_tables import *
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *


SECTION_MARKER_MAP = {
    "Experience Level": ["color", "setup_date", "type", "Incept_date"],
    "Risk Tolerance": ["sharpe_y", "sortino_y", "beta_y", "_1yworstret", "EXITLOAD"],
    "Investment Duration": ["avg_mat_num", "tenure_number", "IsRedeemAvailable", "LockIn", "turnover_ratio"],
    "Decision Making Style": ["expratio", "trackingError", "jalpha_y", "sip"],
    "Emotional Reactions to Market Changes": ["_52weekhhigh", "gross", "ytdret", "adjustednav_c", "_3yworstret"],
    "Research and Professional Advice": ["sebi_reg_no", "trustee_name", "cust_name", "IsPurchaseAvailable", "Benchmark_Weightage"],
    "Sectoral and Investment Preferences": ["asset_type",  "MCAP", "sub_category"]
}

MARKER_MODEL_MAP = {
    MFAMCMaster: ["setup_date", "trustee_name"],
    MFCategoryWiseReturn: ["_1yworstret", "_3yworstret"],
    MFSchemeClassMaster: ["asset_type", "sub_category"],
    MFBenchmarkIndicesAbsoluteReturn: ["ytdret"],
    MFSchemeEquityDetails: ["MCAP"],
    MFCustodianMaster: ["cust_name"],
    MFDividendDetails: ["gross"],
    MFNetAssetValueHighLow: ["_52weekhhigh",],
    MFNetAssetValueHistorical: ["adjustednav_c"],
    MFRatios1Year: ["beta_y", "jalpha_y", "sharpe_y", "sortino_y"],
    MFRatiosDefaultBenchmark1Year: ["trackingError"],
    MFRegistrarMaster: ["sebi_reg_no"],
    MFSchemeAverageMaturity: ["avg_mat_num", "turnover_ratio"],
    MFSchemeEntryExitLoad: ["EXITLOAD"],
    MFSchemeFMPYieldDetails: ["tenure_number"],
    MFSchemeIndexMapping: ["Benchmark_Weightage"],
    MFSchemeMaster: ["color"],
    MFSchemeMasterInDetails: ["Incept_date", "IsPurchaseAvailable", "LockIn","IsRedeemAvailable"], 
    MFSchemeMonthWiseExpenseRatio: ["expratio"],
    MFSystematicInvestmentPlan: ["sip"],
    MFTypeMaster: ["type"],
}


def truncate_table(model):
    table_name = model._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")

def clear_tables():
    """Clear existing data from all relevant tables and reset the auto-increment."""
    truncate_table(MFMarker)
    truncate_table(MFMarkerOptions)
    truncate_table(MFResponse)
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
                )

    print("Section markers populated.")

def populate_marker_options():
    """
    Populate MFMarkerOptions using field data from mapped models based on markers,
    """
    with transaction.atomic():
        for model, marker_fields in MARKER_MODEL_MAP.items():
            for marker_field in marker_fields:
                try:
                    marker_obj = MFMarker.objects.get(marker=marker_field)
                except MFMarker.DoesNotExist:
                    warnings.warn(f"Marker '{marker_field}' not found in MFMarker.")
                    continue
                
                
                # Get distinct non-null values from the model's field
                values = (
                    model.objects.values_list(marker_field, flat=True)
                    .distinct()
                    .exclude(**{f"{marker_field}__isnull": True})
                )

                # check first value to determine datatype
                if values:
                    first_value = values[0]
                else:
                    warnings.warn(f"No values found for marker '{marker_field}' (ID: {marker_obj.id})", UserWarning)
                

                if isinstance(first_value, (datetime, date)):
                    process_datetime_values(values, marker_obj)
                elif isinstance(first_value, (int, float)):
                    process_numeric_values(values, marker_obj)
                elif isinstance(first_value, str):
                    process_text_values(values, marker_obj)
                else:
                    warnings.warn(
                        f"Unexpected type {type(first_value)} for marker '{marker_field}'; treating as text.",
                        UserWarning
                    )
            
    print("MFMarkerOptions populated successfully")

def process_datetime_values(values, marker_obj):
    """Process datetime values and create marker options"""
    now = datetime.now()
    ages = []
    
    for v in values:
        if isinstance(v, (datetime, date)):
            age = now.year - v.year
            ages.append(age)
        else:
            warnings.warn(f"Skipping non date/datetime value")
        
    # Either create bins or use unique values
    if len(ages) > 5:
        create_bins(ages, marker_obj)
    else:
        unique_ages = sorted(set(ages))
        for age in unique_ages:
            create_marker_option(marker_obj, str(age))

def process_numeric_values(values, marker_obj):
    """Process numeric values and create marker options"""
    numeric_values = []
    
    for v in values:
        if isinstance(v, (int, float)):
            numeric_values.append(float(v))
        else:
            warnings.warn(f"Skipping non numeric value")
    
    # Either create bins or use unique values
    if len(numeric_values) > 5:
        create_bins(numeric_values, marker_obj)
    else:
        sorted_values = sorted(numeric_values)
        for value in sorted_values:
            create_marker_option(marker_obj, str(value))

def process_text_values(values, marker_obj):
    """Process text values and create marker options"""
    sorted_values = sorted(str(v) for v in values)
    
    for value in sorted_values:
        create_marker_option(marker_obj, value)

def create_bins(values, marker_obj):
    """Create bins for numeric or datetime values"""
    values_array = np.array(values).reshape(-1, 1)
    
    discretizer = KBinsDiscretizer(n_bins=5, strategy='uniform')
    discretizer.fit(values_array)
    bin_edges = discretizer.bin_edges_[0]
    print(bin_edges)
    
    for i in range(5):
        bin_start = bin_edges[i]
        bin_end = bin_edges[i+1]
        option_label = f"[{bin_start:.2f},{bin_end:.2f}]"
        create_marker_option(marker_obj, option_label)

def create_marker_option(marker_obj, option_value):
    """Create a single marker option"""
    MFMarkerOptions.objects.create(
        section_id=marker_obj.section_id,
        marker_id=marker_obj,
        option=option_value,
    )

def populate_mf_responses():
    Experience_Level_base_query = MFSchemeMasterInDetails.objects.filter(status="Active")

    Experience_Level = ["color", "setup_date", "type", "Incept_date"]

    if "color" in Experience_Level:
        Experience_Level_base_query = Experience_Level_base_query.annotate(
            color=Subquery(
                MFSchemeMaster.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("color")[:1]
            )
        )

    if "setup_date" in Experience_Level:
        Experience_Level_base_query = Experience_Level_base_query.annotate(
            setup_date=Subquery(
                MFAMCMaster.objects.filter(
                    amc_code=OuterRef("amc_code")
                ).values("setup_date")[:1]
            )
        )

    if "type" in Experience_Level:
        Experience_Level_base_query = Experience_Level_base_query.annotate(
            type=Subquery(
                MFTypeMaster.objects.filter(
                    type_code=OuterRef("type_code")
                ).values("type")[:1]
            )
        )

    result_query1 = Experience_Level_base_query.values("schemecode", "color", "setup_date", "type", "Incept_date")

    Risk_Tolerance_base_query = MFSchemeMasterInDetails.objects.filter(status="Active")

    Risk_Tolerance = ["sharpe_y", "sortino_y", "beta_y", "_1yworstret", "EXITLOAD"]

    if "sharpe_y" in Risk_Tolerance:
        Risk_Tolerance_base_query = Risk_Tolerance_base_query.annotate(
            sharpe_y=Subquery(
                MFRatios1Year.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("sharpe_y")[:1]
            )
        )

    if "sortino_y" in Risk_Tolerance:
        Risk_Tolerance_base_query = Risk_Tolerance_base_query.annotate(
            sortino_y=Subquery(
                MFRatios1Year.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("sortino_y")[:1]
            )
        )

    if "beta_y" in Risk_Tolerance:
        Risk_Tolerance_base_query = Risk_Tolerance_base_query.annotate(
            beta_y=Subquery(
                MFRatios1Year.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("beta_y")[:1]
            )
        )

    if "_1yworstret" in Risk_Tolerance:
        Risk_Tolerance_base_query = Risk_Tolerance_base_query.annotate(
            _1yworstret=Subquery(
                MFCategoryWiseReturn.objects.filter(
                    classcode=OuterRef("classcode")
                ).values("_1yworstret")[:1]
            )
        )

    if "EXITLOAD" in Risk_Tolerance:
        Risk_Tolerance_base_query = Risk_Tolerance_base_query.annotate(
            EXITLOAD=Subquery(
                MFSchemeEntryExitLoad.objects.filter(
                    SCHEMECODE=OuterRef("schemecode")
                ).values("EXITLOAD")[:1]
            )
        )

    result_query2 = Risk_Tolerance_base_query.values(
        "schemecode", "sharpe_y", "sortino_y", "beta_y", "_1yworstret", "EXITLOAD"
    )

    Investment_Duration_base_query = MFSchemeMasterInDetails.objects.filter(status="Active")

    Investment_Duration= ["avg_mat_num", "tenure_number", "IsRedeemAvailable", "LockIn", "turnover_ratio"]

    if "avg_mat_num" in Investment_Duration:
        Investment_Duration_base_query = Investment_Duration_base_query.annotate(
            avg_mat_num=Subquery(
                MFSchemeAverageMaturity.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("avg_mat_num")[:1]
            )
        )
    
    if "tenure_number" in Investment_Duration:
        Investment_Duration_base_query = Investment_Duration_base_query.annotate(
            tenure_number=Subquery(
                MFSchemeFMPYieldDetails.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("tenure_number")[:1]
            )
        )
    
    if "turnover_ratio" in Investment_Duration:
        Investment_Duration_base_query = Investment_Duration_base_query.annotate(
            turnover_ratio=Subquery(
                MFSchemeAverageMaturity.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("turnover_ratio")[:1]
            )
        )
    
    result_query3 = Investment_Duration_base_query.values(
        "schemecode", "avg_mat_num", "tenure_number", "IsRedeemAvailable", "LockIn", "turnover_ratio"
    )

    Decision_Making_Style_base_query = MFSchemeMasterInDetails.objects.filter(status="Active")

    Decision_Making_Style = ["expratio", "trackingError", "jalpha_y", "sip"]

    if "expratio" in Decision_Making_Style:
        Decision_Making_Style_base_query = Decision_Making_Style_base_query.annotate(
            expratio=Subquery(
                MFSchemeMonthWiseExpenseRatio.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("expratio")[:1]
            )
        )
    
    if "trackingError" in Decision_Making_Style:
        Decision_Making_Style_base_query = Decision_Making_Style_base_query.annotate(
            trackingError=Subquery(
                MFRatiosDefaultBenchmark1Year.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("trackingError")[:1]
            )
        )
    
    if "jalpha_y" in Decision_Making_Style:
        Decision_Making_Style_base_query = Decision_Making_Style_base_query.annotate(
            jalpha_y=Subquery(
                MFRatios1Year.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("jalpha_y")[:1]
            )
        )
    
    result_query4 = Decision_Making_Style_base_query.values(
        "schemecode", "expratio", "trackingError", "jalpha_y", "sip"
    )

    Emotional_Reactions_to_Market_Changes_base_query = MFSchemeMasterInDetails.objects.filter(status="Active")

    Emotional_Reactions_to_Market_Changes = ["_52weekhhigh", "gross", "ytdret", "adjustednav_c", "_3yworstret"]

    if "_52weekhhigh" in Emotional_Reactions_to_Market_Changes:
        Emotional_Reactions_to_Market_Changes_base_query = Emotional_Reactions_to_Market_Changes_base_query.annotate(
            _52weekhhigh=Subquery(
                MFNetAssetValueHighLow.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("_52weekhhigh")[:1]
            )
        )
    
    if "gross" in Emotional_Reactions_to_Market_Changes:
        Emotional_Reactions_to_Market_Changes_base_query = Emotional_Reactions_to_Market_Changes_base_query.annotate(
            gross=Subquery(
                MFDividendDetails.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("gross")[:1]
            )
        )
    
    if "ytdret" in Emotional_Reactions_to_Market_Changes:
        Emotional_Reactions_to_Market_Changes_base_query = Emotional_Reactions_to_Market_Changes_base_query.annotate(
            ytdret=Subquery(
                MFCategoryWiseReturn.objects.filter(
                    classcode=OuterRef("classcode")
                ).values("ytdret")[:1]
            )
        )
    
    if "adjustednav_c" in Emotional_Reactions_to_Market_Changes:
        Emotional_Reactions_to_Market_Changes_base_query = Emotional_Reactions_to_Market_Changes_base_query.annotate(
            adjustednav_c=Subquery(
                MFNetAssetValueHistorical.objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("adjustednav_c")[:1]
            )
        )
    
    if "_3yworstret" in Emotional_Reactions_to_Market_Changes:
        Emotional_Reactions_to_Market_Changes_base_query = Emotional_Reactions_to_Market_Changes_base_query.annotate(
            _3yworstret=Subquery(
                MFCategoryWiseReturn.objects.filter(
                    classcode=OuterRef("classcode")
                ).values("_3yworstret")[:1]
            )
        )
    
    result_query5 = Emotional_Reactions_to_Market_Changes_base_query.values(
        "schemecode", "_52weekhhigh", "gross", "ytdret", "adjustednav_c", "_3yworstret"
    )

    Research_and_Professional_Advice_base_query = MFSchemeMasterInDetails.objects.filter(status="Active")

    Research_and_Professional_Advice = ["sebi_reg_no", "trustee_name", "cust_name", "IsPurchaseAvailable", "Benchmark_Weightage"]

    if "sebi_reg_no" in Research_and_Professional_Advice:
        Research_and_Professional_Advice_base_query = Research_and_Professional_Advice_base_query.annotate(
            sebi_reg_no=Subquery(
                MFRegistrarMaster.objects.filter(
                    rt_code=OuterRef("rt_code")
                ).values("sebi_reg_no")[:1]
            )
        )
    
    if "trustee_name" in Research_and_Professional_Advice:
        Research_and_Professional_Advice_base_query = Research_and_Professional_Advice_base_query.annotate(
            trustee_name=Subquery(
                MFAMCMaster.objects.filter(
                    amc_code=OuterRef("amc_code")
                ).values("trustee_name")[:1]
            )
        )
    
    if "cust_name" in Research_and_Professional_Advice:
        Research_and_Professional_Advice_base_query = Research_and_Professional_Advice_base_query.annotate(
            cust_name=Subquery(
                MFCustodianMaster.objects.filter(
                    cust_code=OuterRef("cust_code")
                ).values("cust_name")[:1]
            )
        )
    
    if "Benchmark_Weightage" in Research_and_Professional_Advice:
        Research_and_Professional_Advice_base_query = Research_and_Professional_Advice_base_query.annotate(
            Benchmark_Weightage=Subquery(
                MFSchemeIndexMapping.objects.filter(
                    SCHEMECODE=OuterRef("schemecode")
                ).values("Benchmark_Weightage")[:1]
            )
        )

    result_query6 = Research_and_Professional_Advice_base_query.values(
        "schemecode", "sebi_reg_no", "trustee_name", "cust_name", "IsPurchaseAvailable", "Benchmark_Weightage"
    )

    Sectoral_and_Investment_Preferences_base_query = MFSchemeMasterInDetails.objects.filter(status="Active")

    Sectoral_and_Investment_Preferences = ["asset_type", "MCAP", "sub_category"]

    if "asset_type" in Sectoral_and_Investment_Preferences:
        Sectoral_and_Investment_Preferences_base_query = Sectoral_and_Investment_Preferences_base_query.annotate(
            asect_type=Subquery(
                MFSchemeClassMaster.objects.filter(
                    classcode=OuterRef("classcode")
                ).values("asset_type")[:1]
            )
        )
    
    if "MCAP" in Sectoral_and_Investment_Preferences:
        Sectoral_and_Investment_Preferences_base_query = Sectoral_and_Investment_Preferences_base_query.annotate(
            mcap=Subquery(
                MFSchemeEquityDetails.objects.filter(
                    SchemeCode=OuterRef("schemecode")
                ).values("MCAP")[:1]
            )
        )
    
    if "sub_category" in Sectoral_and_Investment_Preferences:
        Sectoral_and_Investment_Preferences_base_query = Sectoral_and_Investment_Preferences_base_query.annotate(
            sub_category=Subquery(
                MFSchemeClassMaster.objects.filter(
                    classcode=OuterRef("classcode")
                ).values("sub_category")[:1]
            )
        )

    result_query7 = Sectoral_and_Investment_Preferences_base_query.values(
        "schemecode", "asect_type", "mcap", "sub_category"
    )
    
    for result_query in [result_query1, result_query2, result_query3, result_query4, result_query5, result_query6, result_query7]:
        for item in result_query:
            schemecode = item['schemecode']
            print(schemecode)
            for key, value in item.items():
                if key == "schemecode":
                    continue
                else:
                    try:
                        marker_obj = MFMarker.objects.get(marker=key)
                        print(f"Marker: {marker_obj.marker}")
                    except MFMarker.DoesNotExist:
                        warnings.warn(f"Marker '{key}' not found in MFMarker.")
                        continue

                    try:
                        option_obj = MFMarkerOptions.objects.filter(
                            section_id=marker_obj.section_id,
                            marker_id=marker_obj,
                        )
                    except MFMarkerOptions.DoesNotExist:
                        warnings.warn(f"Option '{value}' not found for marker '{key}'.")
                        continue
                    
                    final_value = None
                    if isinstance(value, (datetime, date)):
                        now = datetime.now()
                        final_value = now.year - value.year
                    elif isinstance(value, (int, float)):
                        final_value = value
                    elif isinstance(value, str):
                        final_value = value
                    else:
                        warnings.warn(f"Unexpected type {type(value)} for marker '{key}'")
                        continue
                    
                    for option in option_obj:
                        if option.option.startswith("[") and option.option.endswith("]"):
                            option_ranges = option.option[1:-1].split(",")
                            if len(option_ranges) == 2:
                                if float(option_ranges[0]) <= final_value <= float(option_ranges[1]):
                                    MFResponse.objects.create(
                                        scheme_code=schemecode,
                                        marker_id=marker_obj,
                                        option_id=option,
                                        section_id=marker_obj.section_id,
                                    )
                                    print('done')
                                    break
                        elif option.option == str(final_value):
                            MFResponse.objects.create(
                                scheme_code=schemecode,
                                marker_id=marker_obj,
                                option_id=option,
                                section_id=marker_obj.section_id,
                            )
                            print('done')
                            break
                    

def populate_all():
    populate_section_markers()
    populate_marker_options()
    populate_mf_responses()

if __name__ == '__main__':
    clear_tables()  
    populate_all()