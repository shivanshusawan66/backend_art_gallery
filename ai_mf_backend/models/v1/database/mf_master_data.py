from django.db import models

# 1.1 ASSET MANAGEMENT COMPANIES


class MFAMCMaster(models.Model):
    id = models.AutoField(primary_key=True)
    amc_code = models.IntegerField()
    amc = models.CharField(max_length=255)
    fund = models.CharField(max_length=255)
    srno = models.IntegerField()
    office_type = models.CharField(max_length=60)
    add1 = models.TextField(null=True, blank=True)
    add2 = models.TextField(null=True, blank=True)
    add3 = models.TextField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    fax = models.CharField(max_length=255, null=True, blank=True)
    webiste = models.CharField(max_length=255, null=True, blank=True)
    setup_date = models.DateTimeField(null=True, blank=True)
    mf_type = models.CharField(max_length=255, null=True, blank=True)
    trustee_name = models.CharField(max_length=255, null=True, blank=True)
    sponsor_name = models.TextField(null=True, blank=True)
    amc_inc_date = models.DateTimeField(null=True, blank=True)
    s_name = models.CharField(max_length=50, null=True, blank=True)
    amc_symbol = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    rtamccode = models.CharField(max_length=100, null=True, blank=True)
    rtamccode_1 = models.CharField(max_length=100, null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_amc_master"
        verbose_name = "MF AMC Master"
        verbose_name_plural = "MF AMC Masters"
        indexes = [models.Index(fields=["amc_code"])]   


class MFAMCKeyPerson(models.Model):
    id = models.AutoField(primary_key=True)
    amc_code = models.IntegerField()
    amc_name = models.TextField()
    srno = models.IntegerField()
    name = models.CharField(max_length=1000)
    desig = models.CharField(max_length=1000)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_amc_keyperson"
        verbose_name = "MF AMC Key Person"
        verbose_name_plural = "MF AMC Key Persons"
        unique_together = (("amc_code", "srno"),)
        indexes = [
            models.Index(fields=["amc_code", "srno"]),
        ]



# 1.2 SCHEME MASTERS


class MFSchemeMaster(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    amc_code = models.IntegerField(blank=True, null=True)
    scheme_name = models.CharField(max_length=255)
    color = models.CharField(max_length=50)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_master"
        verbose_name = "MF Scheme Master"
        verbose_name_plural = "MF Scheme Masters"
        indexes = [models.Index(fields=["schemecode"])]


class MFSchemeMasterInDetails(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    amfi_code = models.IntegerField(null=True, blank=True)
    cams_code = models.CharField(max_length=50, null=True, blank=True)
    amc_code = models.IntegerField(null=True, blank=True)
    s_name = models.CharField(max_length=255, null=True, blank=True)
    amfi_name = models.CharField(max_length=500, null=True, blank=True)
    isin_code = models.CharField(max_length=50, null=True, blank=True)
    type_code = models.IntegerField(null=True, blank=True)
    opt_code = models.IntegerField(null=True, blank=True)
    classcode = models.IntegerField(null=True, blank=True)
    theme_code = models.IntegerField(null=True, blank=True)
    rt_code = models.IntegerField(null=True, blank=True)
    plan = models.IntegerField(null=True, blank=True)
    cust_code = models.IntegerField(null=True, blank=True)
    cust_code2 = models.IntegerField(null=True, blank=True)
    price_freq = models.IntegerField(null=True, blank=True)
    init_price = models.FloatField(null=True, blank=True)
    offerprice = models.FloatField(null=True, blank=True)
    nfo_open = models.DateTimeField(null=True, blank=True)
    nfo_close = models.DateTimeField(null=True, blank=True)
    reopen_dt = models.DateTimeField(null=True, blank=True)
    elf = models.CharField(max_length=1, null=True, blank=True)
    etf = models.CharField(max_length=1, null=True, blank=True)
    stp = models.CharField(max_length=1, null=True, blank=True)
    primary_fund = models.CharField(max_length=1, null=True, blank=True)
    primary_fd_code = models.IntegerField(null=True, blank=True)
    sip = models.CharField(max_length=1, null=True, blank=True)
    swp = models.CharField(max_length=1, null=True, blank=True)
    switch = models.CharField(max_length=1, null=True, blank=True)
    mininvt = models.FloatField(null=True, blank=True)
    multiples = models.IntegerField(null=True, blank=True)
    inc_invest = models.FloatField(null=True, blank=True)
    adnmultiples = models.FloatField(null=True, blank=True)
    fund_mgr1 = models.CharField(max_length=1000, null=True, blank=True)
    fund_mgr2 = models.CharField(max_length=1000, null=True, blank=True)
    fund_mgr3 = models.CharField(max_length=1000, null=True, blank=True)
    fund_mgr4 = models.CharField(max_length=1000, null=True, blank=True)
    since = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    cutsub = models.CharField(max_length=10, null=True, blank=True)
    cutred = models.CharField(max_length=10, null=True, blank=True)
    red = models.CharField(max_length=50, null=True, blank=True)
    mob_name = models.CharField(max_length=255, null=True, blank=True)
    div_freq = models.IntegerField(null=True, blank=True)
    scheme_symbol = models.CharField(max_length=50, null=True, blank=True)
    fund_mgr_code1 = models.IntegerField(null=True, blank=True)
    FUND_MGR_CODE2 = models.IntegerField(null=True, blank=True)
    FUND_MGR_CODE3 = models.IntegerField(null=True, blank=True)
    FUND_MGR_CODE4 = models.IntegerField(null=True, blank=True)
    Redemption_date = models.DateTimeField(null=True, blank=True)
    DateOfAllot = models.DateTimeField(null=True, blank=True)
    Div_Code = models.FloatField(null=True, blank=True)
    LegalNames = models.CharField(max_length=255, null=True, blank=True)
    AMFIType = models.CharField(max_length=50, null=True, blank=True)
    NonTxnDay = models.CharField(max_length=4, null=True, blank=True)
    SchemeBank = models.CharField(max_length=255, null=True, blank=True)
    SchemeBankAccountNumber = models.CharField(max_length=50, null=True, blank=True)
    SchemeBankBranch = models.CharField(max_length=255, null=True, blank=True)
    DividendOptionFlag = models.CharField(max_length=1, null=True, blank=True)
    LockIn = models.CharField(max_length=50, null=True, blank=True)
    IsPurchaseAvailable = models.CharField(max_length=1, null=True, blank=True)
    IsRedeemAvailable = models.CharField(max_length=1, null=True, blank=True)
    MinRedemptionAmount = models.FloatField(null=True, blank=True)
    RedemptionMultipleAmount = models.FloatField(null=True, blank=True)
    MinRedemptionUnits = models.FloatField(null=True, blank=True)
    RedemptionMultiplesUnits = models.FloatField(null=True, blank=True)
    MinSwitchAmount = models.FloatField(null=True, blank=True)
    SwitchMultipleAmount = models.FloatField(null=True, blank=True)
    MinSwitchUnits = models.FloatField(null=True, blank=True)
    SwitchMultiplesUnits = models.FloatField(null=True, blank=True)
    securitycode = models.CharField(max_length=50, null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    SwitchOut = models.CharField(max_length=1, null=True, blank=True)
    MinSwitchOutAmount = models.FloatField(null=True, blank=True)
    SwitchOutMultipleAmount = models.FloatField(null=True, blank=True)
    MinSwitchOutUnits = models.FloatField(null=True, blank=True)
    SwitchOutMultiplesUnits = models.FloatField(null=True, blank=True)
    Incept_date = models.DateTimeField(null=True, blank=True)
    Incept_Nav = models.FloatField(null=True, blank=True)
    DefaultOpt = models.CharField(max_length=50, null=True, blank=True)
    DefaultPlan = models.CharField(max_length=50, null=True, blank=True)
    LockPeriod = models.IntegerField(null=True, blank=True)
    ODDraftDate = models.DateTimeField(null=True, blank=True)
    Liquidated_Date = models.DateTimeField(null=True, blank=True)
    Old_Plan = models.IntegerField(null=True, blank=True)
    Direct_Plan = models.IntegerField(null=True, blank=True)
    optionType = models.CharField(max_length=10, null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_master_in_details"
        verbose_name = "MF Scheme Master In Detail"
        verbose_name_plural = "MF Scheme Master In Details"
        indexes = [
            models.Index(fields=["schemecode"]),
        ]

class MFSchemeRTCode(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    rtschemecode = models.CharField(max_length=100, null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_rt_code"
        verbose_name = "MF Scheme RT Code"
        verbose_name_plural = "MF Scheme RT Codes"
        indexes = [
            models.Index(fields=["schemecode"]),
        ]

class MFSchemeIsInMaster(models.Model):
    id = models.AutoField(primary_key=True)
    Id = models.IntegerField()
    ISIN = models.CharField(max_length=100)
    Schemecode = models.IntegerField()
    Amc_code = models.IntegerField()
    NseSymbol = models.CharField(max_length=100, null=True, blank=True)
    Series = models.CharField(max_length=50, null=True, blank=True)
    RTASchemecode = models.CharField(max_length=50, null=True, blank=True)
    AMCSchemecode = models.CharField(max_length=50, null=True, blank=True)
    LongSchemeDescrip = models.CharField(max_length=255, null=True, blank=True)
    ShortSchemeDescrip = models.CharField(max_length=255, null=True, blank=True)
    Status = models.CharField(max_length=10, null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_is_in_master"
        verbose_name = "MF Scheme ISIN Master"
        verbose_name_plural = "MF Scheme ISIN Masters"
        indexes = [
            models.Index(fields=["ISIN"]),
        ]

class MFTypeMaster(models.Model):
    id = models.AutoField(primary_key=True)
    type_code = models.IntegerField()
    type = models.CharField(max_length=50)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_type_master"
        verbose_name = "MF Type Master"
        verbose_name_plural = "MF Type Masters"
        indexes = [
            models.Index(fields=["type_code"]),
        ]


class MFOptionMaster(models.Model):
    id = models.AutoField(primary_key=True)
    opt_code = models.IntegerField()
    option = models.CharField(max_length=30)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_option_master"
        verbose_name = "MF Option Master"
        verbose_name_plural = "MF Option Masters"
        indexes = [ 
            models.Index(fields=["opt_code"]),
        ]

    def __str__(self):
        return self.option


class MFSchemeClassMaster(models.Model):
    id = models.AutoField(primary_key=True)
    classcode = models.IntegerField()
    classname = models.CharField(max_length=500)
    asset_code = models.IntegerField()
    asset_type = models.CharField(max_length=500)
    category = models.CharField(max_length=500)
    sub_category = models.CharField(max_length=500, null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_class_master"
        verbose_name = "MF Scheme Class Master"
        verbose_name_plural = "MF Scheme Class Masters"
        indexes = [
            models.Index(fields=["classcode"]),
        ]

class MFRegistrarMaster(models.Model):
    id = models.AutoField(primary_key=True)
    rt_code = models.IntegerField()
    rt_name = models.CharField(max_length=100)
    sebi_reg_no = models.CharField(max_length=50, null=True, blank=True)
    address1 = models.TextField(null=True, blank=True)
    address2 = models.TextField(null=True, blank=True)
    address3 = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    tel = models.TextField(null=True, blank=True)
    fax = models.TextField(null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    reg_address = models.TextField(null=True, blank=True)
    email = models.CharField(max_length=500, null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_registrar_master"
        verbose_name = "MF Registrar Master"
        verbose_name_plural = "MF Registrar Masters"
        indexes = [
            models.Index(fields=["rt_code"])
        ]

class MFPlanMaster(models.Model):
    id = models.AutoField(primary_key=True)
    plan_code = models.IntegerField()
    plan = models.CharField(max_length=50)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_plan_master"
        verbose_name = "MF Plan Master"
        verbose_name_plural = "MF Plan Masters"
        indexes = [
            models.Index(fields=["plan_code"])
        ]


class MFCustodianMaster(models.Model):
    id = models.AutoField(primary_key=True)
    cust_code = models.IntegerField()
    cust_name = models.CharField(max_length=100)
    sebi_reg_no = models.CharField(max_length=25)
    add1 = models.TextField()
    add2 = models.TextField()
    add3 = models.TextField()
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_custodian_master"
        verbose_name = "MF Custodian Master"
        verbose_name_plural = "MF Custodian Masters"
        indexes = [
            models.Index(fields=["cust_code"])
        ]


class MFFundManagerMaster(models.Model):
    id = models.AutoField(primary_key=True)
    initial = models.CharField(max_length=10)
    fundmanager = models.CharField(max_length=200)
    qualification = models.CharField(max_length=200, null=True, blank=True)
    experience = models.CharField(max_length=200, null=True, blank=True)
    basicdetails = models.CharField(max_length=1000, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    reporteddate = models.DateTimeField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_fundmanager_master"
        verbose_name = "MF Fund Manager Master"
        verbose_name_plural = "MF Fund Manager Masters"


class MFDividendMaster(models.Model):
    id = models.AutoField(primary_key=True)
    div_code = models.FloatField()
    div_type = models.CharField(max_length=30)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_dividend_master"
        verbose_name = "MF Dividend Master"
        verbose_name_plural = "MF Dividend Masters"
        indexes = [
            models.Index(fields=["div_code"])
        ]


# 1.3 SCHEME OBJECTIVE


class MFSchemeObjective(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    objective = models.TextField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_objective"
        verbose_name = "MF Scheme Objective"
        verbose_name_plural = "MF Scheme Objectives"
        indexes = [
            models.Index(fields=["schemecode"])
        ]


# 1.4.1 SYSTEMATIC INVESTMENT PLAN


class MFSystematicInvestmentPlan(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    amc_code = models.IntegerField(null=True, blank=True)
    frequency = models.CharField(max_length=100)
    sip = models.CharField(max_length=1)
    sipdatescondition = models.CharField(max_length=8000, null=True, blank=True)
    Dates = models.CharField(max_length=8000, null=True, blank=True)
    sipdaysall = models.CharField(max_length=50, null=True, blank=True)
    sipmininvest = models.FloatField(null=True, blank=True)
    sipaddninvest = models.FloatField(null=True, blank=True)
    sipfrequencyno = models.IntegerField(null=True, blank=True)
    sipminimumperiod = models.IntegerField(null=True, blank=True)
    sipmaximumperiod = models.CharField(max_length=100, null=True, blank=True)
    sipmincumamount = models.CharField(max_length=100, null=True, blank=True)
    sipminunits = models.FloatField(null=True, blank=True)
    sipmultiplesunits = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_systematic_investment_plan"
        verbose_name = "MF Systematic Investment Plan"
        verbose_name_plural = "MF Systematic Investment Plan"
        unique_together = ("schemecode", "frequency")
        indexes = [
            models.Index(fields=["schemecode", "frequency"])
        ]

class MFSystematicWithdrawalPlan(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    amc_code = models.IntegerField(null=True, blank=True)
    frequency = models.CharField(max_length=100)
    swp = models.CharField(max_length=1)
    swpdatescondition = models.CharField(max_length=8000, null=True, blank=True)
    Dates = models.CharField(max_length=8000, null=True, blank=True)
    swpdaysall = models.CharField(max_length=50, null=True, blank=True)
    swpmininvest = models.FloatField(null=True, blank=True)
    swpaddninvest = models.FloatField(null=True, blank=True)
    swpfrequencyno = models.IntegerField(null=True, blank=True)
    swpminimumperiod = models.IntegerField(null=True, blank=True)
    swpmaximumperiod = models.CharField(max_length=100, null=True, blank=True)
    swpmincumamount = models.CharField(max_length=100, null=True, blank=True)
    swpminunits = models.FloatField(null=True, blank=True)
    swpmultiplesunits = models.FloatField(null=True, blank=True)
    Flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_systematic_withdrawal_plan"
        verbose_name = "MF Systematic Withdrawal Plan"
        verbose_name_plural = "MF Systematic Withdrawal Plan"
        unique_together = ("schemecode", "frequency")
        indexes = [
            models.Index(fields=["schemecode", "frequency"])
        ]


class MFSystematicTransferPlan(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    amc_code = models.IntegerField(null=True, blank=True)
    frequency = models.CharField(max_length=100)
    stpinout = models.CharField(max_length=1)
    stp = models.CharField(max_length=1)
    stpdatescondition = models.CharField(max_length=8000, null=True, blank=True)
    Dates = models.CharField(max_length=8000, null=True, blank=True)
    stpdaysall = models.CharField(max_length=50, null=True, blank=True)
    stpmininvest = models.FloatField(null=True, blank=True)
    stpaddninvest = models.FloatField(null=True, blank=True)
    stpfrequencyno = models.IntegerField(null=True, blank=True)
    stpminimumperiod = models.IntegerField(null=True, blank=True)
    stpmaximumperiod = models.CharField(max_length=100, null=True, blank=True)
    stpmincumamount = models.CharField(max_length=100, null=True, blank=True)
    stpminunits = models.FloatField(null=True, blank=True)
    stpmultiplesunits = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_systematic_transfer_plan"
        verbose_name = "MF Systematic Transfer Plan"
        verbose_name_plural = "MF Systematic Transfer Plan"
        unique_together = ("schemecode", "frequency", "stpinout")
        indexes = [
            models.Index(fields=["schemecode", "frequency", "stpinout"])
        ]


# 1.5 SCHEME BENCHMARK INDEX


class MFSchemeIndexMapping(models.Model):
    id = models.AutoField(primary_key=True)
    SCHEMECODE = models.IntegerField()
    INDEXCODE = models.IntegerField()
    Benchmark_Weightage = models.FloatField(null=True, blank=True)
    IndexOrder = models.IntegerField(null=True, blank=True)
    Remark = models.CharField(max_length=100, null=True, blank=True)
    FLAG = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_index_mapping"
        verbose_name = "MF Scheme Index Mapping"
        verbose_name_plural = "MF Scheme Index Mappings"
        unique_together = ("SCHEMECODE", "INDEXCODE")
        indexes = [
            models.Index(fields=["SCHEMECODE", "INDEXCODE"])
        ]


class MFIndexMaster(models.Model):
    id = models.AutoField(primary_key=True)
    indexcode = models.IntegerField()
    fincode = models.IntegerField(null=True, blank=True)
    scripcode = models.IntegerField(null=True, blank=True)
    indexname = models.CharField(max_length=255)
    index_gp = models.CharField(max_length=250)
    subgroup = models.CharField(max_length=250)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_index_master"
        verbose_name = "MF Index Master"
        verbose_name_plural = "MF Index Masters"
        indexes = [
            models.Index(fields=["indexcode"])
        ]


# 1.6 SCHEME ENTRY EXIT LOAD


class MFSchemeEntryExitLoad(models.Model):
    id = models.AutoField(primary_key=True)
    SCHEMECODE = models.IntegerField()
    LDATE = models.DateTimeField(null=True, blank=True)
    LTYPECODE = models.IntegerField(null=True, blank=True)
    LSRNO = models.IntegerField()
    FRMAMOUNT = models.FloatField(blank=True, null=True)
    UPTOAMOUNT = models.FloatField(null=True, blank=True)
    MINPERIOD = models.IntegerField(null=True, blank=True)
    MAXPERIOD = models.IntegerField(null=True, blank=True)
    MIN = models.CharField(max_length=10, null=True, blank=True)
    MAX = models.CharField(max_length=10, null=True, blank=True)
    ENTRYLOAD = models.FloatField(null=True, blank=True)
    EXITLOAD = models.FloatField(null=True, blank=True)
    REMARKS = models.TextField(null=True, blank=True)
    Period_Condition = models.CharField(max_length=10, null=True, blank=True)
    Period_Type = models.CharField(max_length=10, null=True, blank=True)
    Period = models.CharField(max_length=100, null=True, blank=True)
    Amount_Condition = models.CharField(max_length=10, null=True, blank=True)
    Amount_Type = models.CharField(max_length=10, null=True, blank=True)
    Per_Condition = models.CharField(max_length=10, null=True, blank=True)
    Per_Frm = models.FloatField(null=True, blank=True)
    Per_To = models.FloatField(null=True, blank=True)
    FLAG = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_entry_exit_load"
        verbose_name = "MF Scheme Entry Exit Load"
        verbose_name_plural = "MF Scheme Entry Exit Load"
        unique_together = (("SCHEMECODE", "LDATE", "LTYPECODE", "LSRNO"),)
        indexes = [
            models.Index(fields=["SCHEMECODE", "LDATE", "LTYPECODE", "LSRNO"])
        ]


class MFLoadTypeMaster(models.Model):
    id = models.AutoField(primary_key=True)
    ltypecode = models.IntegerField()
    load = models.CharField(max_length=20)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_loadtype_master"
        verbose_name = "MF Load Type Master"
        verbose_name_plural = "MF Load Type Masters"
        indexes = [
            models.Index(fields=["ltypecode"])
        ]


# 1.7 PORTFOLIO MASTERS


class MFCompanyMaster(models.Model):
    id = models.AutoField(primary_key=True)
    fincode = models.IntegerField()
    scripcode = models.IntegerField(null=True, blank=True)
    symbol = models.CharField(max_length=50, null=True, blank=True)
    compname = models.CharField(max_length=255, null=True, blank=True)
    s_name = models.CharField(max_length=100, null=True, blank=True)
    ind_code = models.IntegerField(null=True, blank=True)
    Industry = models.CharField(max_length=100, null=True, blank=True)
    isin = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    series = models.CharField(max_length=2, null=True, blank=True)
    listing = models.CharField(max_length=50, null=True, blank=True)
    sublisting = models.CharField(max_length=50, null=True, blank=True)
    fv = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_company_master"
        verbose_name = "MF Company Master"
        verbose_name_plural = "MF Company Masters"
        indexes = [
            models.Index(fields=["fincode"])
        ]


class MFIndustryMaster(models.Model):
    id = models.AutoField(primary_key=True)
    Ind_code = models.IntegerField()
    Industry = models.CharField(max_length=255)
    Ind_shortname = models.CharField(max_length=255)
    Sector = models.CharField(max_length=255)
    Sector_code = models.IntegerField()
    Flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_industry_master"
        verbose_name = "MF Industry Master"
        verbose_name_plural = "MF Industry Masters"
        indexes = [
            models.Index(fields=["Ind_code"])
        ]


class MFAssetAllocationMaster(models.Model):
    id = models.AutoField(primary_key=True)
    asect_code = models.FloatField()
    asect_type = models.CharField(max_length=100)
    asset = models.CharField(max_length=50)
    as_name = models.CharField(max_length=50)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_asset_allocation_master"
        verbose_name = "MF Asset Allocation Master"
        verbose_name_plural = "MF Asset Allocation Masters"
        indexes = [
            models.Index(fields=["asect_code"])
        ]


# 1.8 RAJIV GANDHI EQUITY SAVING SCHEMES


class MFSchemeRGESS(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    schemename = models.CharField(max_length=255)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_rgess"
        verbose_name = "MF Scheme RGESS"
        verbose_name_plural = "MF Scheme RGESS"
        indexes = [
            models.Index(fields=["schemecode"])
        ]
