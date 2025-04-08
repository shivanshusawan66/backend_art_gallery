import os
import sys
from itertools import chain
import django
import ijson
from datetime import datetime

from django.db import transaction, models, connection, connections
from django.utils import timezone



BASE_TXT_DIR = os.path.join(os.getcwd(), "..", "MutualFund")
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings")
django.setup()

from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *


MODEL_FILE_MAPPING = {
    # Asset Management Companies (2)
    MFAMCMaster: f"{BASE_TXT_DIR}\\Amc_mst_new.txt",
    MFAMCKeyPerson: f"{BASE_TXT_DIR}\\Amc_keypersons.txt",
    
    # Scheme Masters (12)
    MFSchemeMaster: f"{BASE_TXT_DIR}\\Scheme_master.txt",
    MFSchemeMasterInDetails: f"{BASE_TXT_DIR}\\Scheme_details.txt",
    MFSchemeRTCode: f"{BASE_TXT_DIR}\\Scheme_rtcode.txt",
    MFSchemeIsInMaster: f"{BASE_TXT_DIR}\\schemeisinmaster.txt",
    MFTypeMaster: f"{BASE_TXT_DIR}\\Type_mst.txt",
    MFOptionMaster: f"{BASE_TXT_DIR}\\Option_mst.txt",
    MFSchemeClassMaster: f"{BASE_TXT_DIR}\\Sclass_mst.txt",
    MFRegistrarMaster: f"{BASE_TXT_DIR}\\Rt_mst.txt",
    MFPlanMaster: f"{BASE_TXT_DIR}\\Plan_mst.txt",
    MFCustodianMaster: f"{BASE_TXT_DIR}\\Cust_mst.txt",
    MFFundManagerMaster: f"{BASE_TXT_DIR}\\Fundmanager_mst.txt",
    MFDividendMaster: f"{BASE_TXT_DIR}\\Div_mst.txt",
    
    # Scheme Objective (1)
    MFSchemeObjective: f"{BASE_TXT_DIR}\\Scheme_objective.txt",
    
    # SIP / STP / SWP Details (3)
    MFSystematicInvestmentPlan: f"{BASE_TXT_DIR}\\Mf_sip.txt",
    MFSystematicWithdrawalPlan: f"{BASE_TXT_DIR}\\Mf_swp.txt",
    MFSystematicTransferPlan: f"{BASE_TXT_DIR}\\Mf_stp.txt",
    
    # Scheme Benchmark Index (2)
    MFSchemeIndexMapping: f"{BASE_TXT_DIR}\\Scheme_index_part.txt",
    MFIndexMaster: f"{BASE_TXT_DIR}\\Index_mst.txt",
    
    # Scheme Load (2)
    MFSchemeEntryExitLoad: f"{BASE_TXT_DIR}\\Schemeload.txt",
    MFLoadTypeMaster: f"{BASE_TXT_DIR}\\Loadtype_mst.txt",
    
    # Portfolio Masters (3)
    MFCompanyMaster: f"{BASE_TXT_DIR}\\Companymaster.txt",
    MFIndustryMaster: f"{BASE_TXT_DIR}\\Industry_mst.txt",
    MFAssetAllocationMaster: f"{BASE_TXT_DIR}\\Asect_mst.txt",
    
    # Rajiv Gandhi Equity Savings Schemes (1)
    MFSchemeRGESS: f"{BASE_TXT_DIR}\\Scheme_rgess.txt",

    # Portfolio (7)
    MFPortfolio: f"{BASE_TXT_DIR}\\Mf_portfolio.txt",
    MFAMCPortfolioAUM: f"{BASE_TXT_DIR}\\Amc_paum.txt",
    MFSchemePortfolioAUM: f"{BASE_TXT_DIR}\\Scheme_paum.txt",
    MFAMCAUM: f"{BASE_TXT_DIR}\\amc_aum.txt",
    MFSchemeAUM: f"{BASE_TXT_DIR}\\scheme_aum.txt",
    MFPortfolioInOut: f"{BASE_TXT_DIR}\\Portfolio_inout.txt",
    MFAverageSchemeAUM: f"{BASE_TXT_DIR}\\Avg_scheme_aum.txt",

    # Net Asset Value (3)
    MFNSEAssetValueLatest: f"{BASE_TXT_DIR}\\Currentnav.txt",
    MFNetAssetValueHistorical: [
        f"{BASE_TXT_DIR}\\Navhist_01.txt",
        f"{BASE_TXT_DIR}\\Navhist_02.txt",
        f"{BASE_TXT_DIR}\\Navhist_03.txt",
        f"{BASE_TXT_DIR}\\Navhist_04.txt",
        f"{BASE_TXT_DIR}\\Navhist_05.txt",
        f"{BASE_TXT_DIR}\\Navhist_06.txt",
        f"{BASE_TXT_DIR}\\Navhist_07.txt",
        f"{BASE_TXT_DIR}\\Navhist_08.txt",
        f"{BASE_TXT_DIR}\\Navhist_09.txt",
        f"{BASE_TXT_DIR}\\Navhist_10.txt",
        f"{BASE_TXT_DIR}\\Navhist_11.txt",
        f"{BASE_TXT_DIR}\\Navhist_12.txt",
        f"{BASE_TXT_DIR}\\Navhist_13.txt",
        f"{BASE_TXT_DIR}\\Navhist_14.txt",
        f"{BASE_TXT_DIR}\\Navhist_15.txt",
    ],
    MFNetAssetValueHighLow: f"{BASE_TXT_DIR}\\Navhist_HL.txt",

    # Returns (7)
    MFReturn: f"{BASE_TXT_DIR}\\Mf_return.txt",
    MFAbsoluteReturn: f"{BASE_TXT_DIR}\\Mf_abs_return.txt",
    MFAnnualizedReturn: f"{BASE_TXT_DIR}\\Mf_ans_return.txt",
    MFCAGRReturn: f"{BASE_TXT_DIR}\\Mf_cagr_return.txt",
    MFCategoryWiseReturn: f"{BASE_TXT_DIR}\\ClassWiseReturn.txt",
    MFBenchmarkIndicesAbsoluteReturn: f"{BASE_TXT_DIR}\\BM_AbsoluteReturn.txt",
    MFBenchmarkIndicesAnnualisedReturn: f"{BASE_TXT_DIR}\\BM_AnnualisedReturn.txt",

    # Ratios (3)
    MFRatios1Year: f"{BASE_TXT_DIR}\\Mf_ratio.txt",
    MFRatiosDefaultBenchmark1Year: f"{BASE_TXT_DIR}\\MF_Ratios_DefaultBM.txt",
    MFRatios3Year: f"{BASE_TXT_DIR}\\Ratio_3Year_MonthlyRet.txt",
 
    # Dividend (1)
    MFDividendDetails: f"{BASE_TXT_DIR}\\Divdetails.txt",

    # Additional (11)
    MFSchemeMonthWiseExpenseRatio: f"{BASE_TXT_DIR}\\Expenceratio.txt",
    MFSchemeEquityDetails: f"{BASE_TXT_DIR}\\Scheme_eq_details.txt",
    MFSchemeFMPYieldDetails: f"{BASE_TXT_DIR}\\fmp_yielddetails.txt",
    MFSchemeAverageMaturity: f"{BASE_TXT_DIR}\\Avg_maturity.txt",
    MFFaceValueChange: f"{BASE_TXT_DIR}\\Fvchange.txt",
    MFSchemeNameChange: f"{BASE_TXT_DIR}\\Scheme_Name_Change.txt",
    MFFundmanager: f"{BASE_TXT_DIR}\\DailyFundmanager.txt",
    MFMergedschemes: f"{BASE_TXT_DIR}\\Mergedschemes.txt",
    MFBulkDeals: f"{BASE_TXT_DIR}\\MFBULKDEALS.txt",
    MFSchemeAssetAllocation: f"{BASE_TXT_DIR}\\Scheme_assetalloc.txt",
    MFCompanyMcap: f"{BASE_TXT_DIR}\\CompanyMcap.txt",
}


BATCH_SIZE = 20000  

def reset_pk_sequence(model):
    table_name = model._meta.db_table
    sequence_sql = f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;"
    with connection.cursor() as cursor:
        cursor.execute(sequence_sql)

def clear_tables(models_list):
    with transaction.atomic():
        for model in models_list:
            model.objects.all().delete()
            reset_pk_sequence(model)

def create_field_mapping(model_fields, json_columns):
    mapping = {}
    for field_name in model_fields:
        if field_name in json_columns:
            mapping[field_name] = field_name
        elif field_name.startswith('_') and field_name[1:] in json_columns:
            mapping[field_name] = field_name[1:]
    return mapping

def create_field_converters(model_fields, json_columns):
    converters = []
    field_mapping = create_field_mapping(model_fields, json_columns)
    
    for model_field in model_fields.values():
        json_key = field_mapping.get(model_field.name)
        if not json_key:
            continue

        field = model_field
        if isinstance(field, models.DateTimeField):
            def make_datetime_converter():
                field_type = 'datetime'
                def converter(value):
                    if not value or value.lower() == 'null':
                        return None
                    try:
                        cleaned = value.split('.')[0]
                        dt = datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S")
                        return timezone.make_aware(dt)
                    except:
                        return None
                return converter
            converters.append((model_field.name, json_key, make_datetime_converter()))
        
        elif isinstance(field, models.DateField):
            def make_date_converter():
                def converter(value):
                    if not value or value.lower() == 'null':
                        return None
                    try:
                        return datetime.strptime(value, "%Y-%m-%d").date()
                    except:
                        return None
                return converter
            converters.append((model_field.name, json_key, make_date_converter()))
        
        elif isinstance(field, (models.IntegerField, models.FloatField)):
            def make_number_converter():
                def converter(value):
                    try:
                        return float(value.replace(',', '')) if value else None
                    except:
                        return None
                return converter
            converters.append((model_field.name, json_key, make_number_converter()))
        
        else:
            def make_string_converter():
                def converter(value):
                    return str(value).strip() if value else None
                return converter
            converters.append((model_field.name, json_key, make_string_converter()))
    
    return converters

def process_file(model, file_path):
    file_name = os.path.basename(file_path)
    model_name = model.__name__
    print(f"\nProcessing: {model_name} - {file_name}")
    count = 0
    errors = 0
    warning_count = 0

    try:
        # First pass to count records
        with open(file_path, 'rb') as f:
            total_records = sum(1 for _ in ijson.items(f, 'Table.item'))
            print(f"Records to process: {total_records}")
        
        # Second pass to import data
        with open(file_path, 'rb') as f:
            items = ijson.items(f, 'Table.item')
            first_record = next(items, None)
            
            if not first_record:
                print(f"ERROR: Empty file.")
                return 0, 0

            # Validate and setup
            json_columns = first_record.keys()
            is_valid, validation_msg = validate_fields(model, json_columns)
            if not is_valid:
                print(f"ERROR: Validation failed: {validation_msg}")
                return 0, 0

            model_fields = {f.name: f for f in model._meta.fields if not f.auto_created}
            converters = create_field_converters(model_fields, json_columns)
            
            # Process records
            all_items = chain([first_record], items)
            batch = []
            milestone = total_records // 10  # Report at each 10%
            
            for i, record in enumerate(all_items):
                try:
                    # Create model instance
                    obj = model()
                    for field_name, json_key, converter in converters:
                        if field_name == "id" or field_name == "created_at":  
                            continue
                        value = record.get(json_key)
                        converted_value = converter(value)
                        
                        # Check for potential data issues
                        if value and converted_value is None:
                            warning_count += 1
                            if warning_count <= 5:  # Limit warning output
                                print(f"WARNING: Could not convert '{value}' for field '{field_name}' at record {i}")
                            elif warning_count == 6:
                                print("Additional warnings suppressed...")
                                
                        setattr(obj, field_name, converted_value)
                    batch.append(obj)
                    
                    # Show simple progress at 10% intervals
                    if milestone > 0 and i % milestone == 0:
                        percent = (i // milestone) * 10
                        print(f"{file_name}: {percent}% done")
                    
                    # Bulk create when batch is full
                    if len(batch) >= BATCH_SIZE:
                        try:
                            with transaction.atomic():
                                model.objects.bulk_create(batch)
                            count += len(batch)
                        except Exception as e:
                            errors += 1
                            print(f"ERROR: Batch insert failed: {str(e)[:150]}")
                            # Try to insert one by one to identify problematic records
                            for single_obj in batch:
                                try:
                                    single_obj.save()
                                    count += 1
                                except Exception as e2:
                                    errors += 1
                                    if errors <= 10:
                                        print(f"ERROR: Record insert failed: {str(e2)[:150]}")
                        batch = []
                        
                except Exception as e:
                    errors += 1
                    if errors <= 10:  # Limit error output
                        print(f"ERROR: Processing record {i}: {str(e)[:150]}")
            
            # Process remaining records
            if batch:
                try:
                    with transaction.atomic():
                        model.objects.bulk_create(batch)
                    count += len(batch)
                except Exception as e:
                    errors += 1
                    print(f"ERROR: Final batch insert failed: {str(e)[:150]}")
                    # Try individual records
                    for single_obj in batch:
                        try:
                            single_obj.save()
                            count += 1
                        except Exception:
                            errors += 1
                
            print(f"{file_name}: 100% done")
                
    except Exception as e:
        print(f"CRITICAL ERROR: File processing failed: {str(e)}")
        errors += 1
    
    print(f"Completed {file_name}: {count} records processed, {errors} errors, {warning_count} warnings")
    return count, errors

def validate_fields(model, json_columns):
    model_fields = {f.name: f for f in model._meta.fields if not f.auto_created}
    required_fields = [f.name for f in model_fields.values() 
                  if not f.null and not f.has_default() and f.name != "id" and f.name != "created_at"]
    
    for field in required_fields:
        if field not in json_columns and f'_{field}' not in json_columns:
            return False, f"Missing required field: {field}"
    
    return True, ""

def import_data(clear_first=True):
    models_to_import = list(MODEL_FILE_MAPPING.keys())  
    
    if clear_first:
        print("Clearing existing data...")
        clear_tables(models_to_import)
    
    start_time = datetime.now()
    total = 0
    errors = 0
    
    print(f"Starting import at {start_time.strftime('%H:%M:%S')}")
    
    # Process models sequentially in defined order
    for model in models_to_import:
        file_paths = MODEL_FILE_MAPPING[model]
        if not isinstance(file_paths, list):
            file_paths = [file_paths]
        
        # Process each file for this model sequentially
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            
            # Process single file
            success, err = process_file(model, file_path)
            total += success
            errors += err
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\nImport completed at {end_time.strftime('%H:%M:%S')}")
    print(f"Duration: {duration}")
    print(f"Total inserted: {total} | Errors: {errors}")


if __name__ == '__main__':
    # Close connections before starting (for any potential prefork setups)
    for conn in connections.all():
        conn.close()
    
    import_data(input("Clear existing data? (y/n): ").lower() == 'y')