from django.db import models


#  ADDITIONAL

class MFSchemeMonthWiseExpenseRatio(models.Model):
    id = models.AutoField(primary_key=True)
    amc_code = models.IntegerField(blank=True, null=True)
    schemecode = models.IntegerField()
    date = models.DateTimeField(blank=True, null=True)
    expratio = models.FloatField(blank=True, null=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_month_wise_expense_ratio"
        verbose_name = "MF Scheme Month Wise Expense Ratio"
        verbose_name_plural = "MF Scheme Month Wise Expense Ratio"
        unique_together = (('schemecode', 'date'),)

class MFSchemeEquityDetails(models.Model):
    id = models.AutoField(primary_key=True)
    SchemeCode = models.IntegerField()
    MonthEnd = models.IntegerField(blank=True, null=True)
    MCAP = models.FloatField(blank=True, null=True)
    PE = models.FloatField(blank=True, null=True)
    PB = models.FloatField(blank=True, null=True)
    Div_Yield = models.FloatField(blank=True, null=True) 
    FLAG = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_equity_details"
        verbose_name = "MF Scheme Equity Detail"
        verbose_name_plural = "MF Scheme Equity Details"
    
class MFSchemeFMPYieldDetails(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    maturitydate = models.DateTimeField(blank=True, null=True)
    tenure_number = models.FloatField(blank=True, null=True)
    tenure_option = models.CharField(max_length=10, blank=True, null=True)
    net_initcative_yield1 = models.FloatField(null=True, blank=True)
    net_initcative_yield2 = models.FloatField(null=True, blank=True)
    post_taxyield_ind1 = models.FloatField(null=True, blank=True)
    post_taxyield_ind2 = models.FloatField(null=True, blank=True)
    post_taxyield_nonind1 = models.FloatField(null=True, blank=True)
    post_taxyield_nonind2 = models.FloatField(null=True, blank=True)
    exit_load = models.CharField(max_length=30, blank=True, null=True)
    rollover = models.CharField(max_length=1, blank=True, null=True)
    maturitydate_after_rollover = models.DateTimeField(blank=True, null=True)
    tenure_no_rollover = models.FloatField(blank=True, null=True)
    tenure_option_rollover = models.CharField(max_length=10, blank=True, null=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_fmp_yield_details"
        verbose_name = "MF Scheme FMP Yield Details"
        verbose_name_plural = "MF Scheme FMP Yield Details"

class MFSchemeAverageMaturity(models.Model):
    id = models.AutoField(primary_key=True)
    amc_code = models.IntegerField()
    schemecode = models.IntegerField()
    date = models.DateTimeField()
    invenddate = models.DateTimeField(blank=True, null=True)
    avg_mat_num = models.FloatField(blank=True, null=True)
    avg_mat_days = models.CharField(max_length=10, blank=True, null=True)
    mod_dur_num = models.FloatField(blank=True, null=True)
    mod_dur_days = models.CharField(max_length=10, blank=True, null=True)
    ytm = models.FloatField(blank=True, null=True)
    turnover_ratio = models.FloatField(blank=True, null=True)
    tr_mode = models.CharField(max_length=10, blank=True, null=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_average_maturity"
        verbose_name = "MF Scheme Average Maturity"
        verbose_name_plural = "MF Scheme Average Maturity"
        unique_together = (('schemecode', 'date'),)

class MFFaceValueChange(models.Model):
    id = models.AutoField(primary_key=True)
    amc_code = models.IntegerField()
    schemecode = models.IntegerField()
    scheme_name = models.CharField(max_length=255, null=True, blank=True)
    fvbefore = models.FloatField()
    fvafter = models.FloatField()
    fvdate = models.DateTimeField()
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_face_value_change"
        verbose_name = "MF Face Value Change"
        verbose_name_plural = "MF Face Value Change"
        unique_together = (('schemecode', 'fvdate'),)

class MFSchemeNameChange(models.Model):
    id = models.AutoField(primary_key=True)
    Amc_Code = models.IntegerField()  
    SchemeCode = models.IntegerField()
    Effectivedate = models.DateTimeField()
    OldName = models.CharField(max_length=255)
    Newname = models.CharField(max_length=255)
    Flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_name_change"
        verbose_name = "MF Scheme Name Change"
        verbose_name_plural = "MF Scheme Name Change"
        unique_together = (('Amc_Code', 'SchemeCode', 'Effectivedate'),)

class MFFundmanager(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    amc = models.IntegerField()
    schemecode = models.IntegerField()
    fundManger1 = models.IntegerField(null=True, blank=True)
    fundManger2 = models.IntegerField(null=True, blank=True)
    fundManger3 = models.IntegerField(null=True, blank=True)
    fundManger4 = models.IntegerField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_fund_manager"
        verbose_name = "MF Fund Manager"
        verbose_name_plural = "MF Fund Manager"
        unique_together = (('date', 'schemecode'),)

class MFMergedschemes(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    mergedwith = models.IntegerField()
    EFFECT_DATE = models.DateTimeField()
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_merged_schemes"
        verbose_name = "MF Merged Scheme"
        verbose_name_plural = "MF Merged Schemes"
        unique_together = (('schemecode', 'mergedwith'),)

class MFBulkDeals(models.Model):
    id = models.AutoField(primary_key=True)
    fincode = models.IntegerField()
    date = models.DateTimeField()
    exchange = models.CharField(max_length=50)
    clientname = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    mfcode = models.IntegerField()
    dealtype = models.CharField(max_length=5)
    volume = models.DecimalField(max_digits=18, decimal_places=0)
    price = models.FloatField()
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_bulk_deals"
        verbose_name = "MF Bulk Deal"
        verbose_name_plural = "MF Bulk Deals"
        unique_together = (('fincode', 'date', 'clientname', 'dealtype', 'volume', 'price'),)

class MFSchemeAssetAllocation(models.Model):
    id = models.AutoField(primary_key=True)
    schemeinv_id = models.IntegerField()
    schemecode = models.IntegerField()
    investment = models.CharField(max_length=500)
    mininv = models.FloatField()
    maxinv = models.FloatField()
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_asset_allocation"
        verbose_name = "MF Scheme Asset Allocation"
        verbose_name_plural = "MF Scheme Asset Allocation"
        unique_together = (('schemecode', 'investment'),)

class MFCompanyMcap(models.Model):
    id = models.AutoField(primary_key=True)
    fincode = models.IntegerField()
    mcap = models.FloatField()
    mode = models.CharField(max_length=20)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_company_mcap"
        verbose_name = "MF Company Mcap"
        verbose_name_plural = "MF Company Mcap"