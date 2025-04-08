from django.db import models


# 1.1 PORTFOLIO

class MFPortfolio(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    invdate = models.DateTimeField(blank=True, null=True)
    invenddate = models.DateTimeField(null=True, blank=True)
    srno = models.IntegerField(null=True, blank=True)
    fincode = models.IntegerField(null=True, blank=True)
    ASECT_CODE = models.IntegerField(null=True, blank=True)
    sect_code = models.IntegerField(null=True, blank=True)
    noshares = models.DecimalField(max_digits=18, decimal_places=0, null=True, blank=True)
    mktval = models.FloatField(null=True, blank=True)
    aum = models.FloatField(null=True, blank=True)
    holdpercentage = models.FloatField(null=True, blank=True)
    compname = models.CharField(max_length=255, null=True, blank=True)
    sect_name = models.CharField(max_length=50, null=True, blank=True)
    asect_name = models.CharField(max_length=50, null=True, blank=True)
    rating = models.CharField(max_length=50, null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_portfolio"
        verbose_name = "MF Portfolio"
        verbose_name_plural = "MF Portfolio"
        unique_together = (('schemecode', 'invdate', 'srno'),)


class MFAMCPortfolioAUM(models.Model):
    id = models.AutoField(primary_key=True)
    amc_code = models.IntegerField()
    aumdate = models.DateTimeField(blank=True, null=True)
    totalaum = models.FloatField(null=True, blank=True)
    FLAG = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_amc_portfolio_aum"
        verbose_name = "MF AMC Portfolio AUM"
        verbose_name_plural = "MF AMC Portfolio AUMs"
        unique_together = (('amc_code', 'aumdate'),)

class MFSchemePortfolioAUM(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    monthend = models.IntegerField(null=True, blank=True)
    amc_code = models.IntegerField(null=True, blank=True)
    aum = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_portfolio_aum"
        verbose_name = "MF Scheme Portfolio AUM"
        verbose_name_plural = "MF Scheme Portfolio AUMs"
        unique_together = (('schemecode', 'monthend'),)

class MFAMCAUM(models.Model):
    id = models.AutoField(primary_key=True)
    amc_code = models.IntegerField()
    aumdate = models.DateTimeField(blank=True, null=True)
    totalaum = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_amc_aum"
        verbose_name = "MF AMC AUM"
        verbose_name_plural = "MF AMC AUMs"
        unique_together = (('amc_code', 'aumdate'),)

class MFSchemeAUM(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    date = models.DateTimeField(null=True, blank=True)
    exfof = models.FloatField(null=True, blank=True)
    fof = models.FloatField(null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_scheme_aum"
        verbose_name = "MF Scheme AUM"
        verbose_name_plural = "MF Scheme AUMs"
        unique_together = (('schemecode', 'date'),)

class MFPortfolioInOut(models.Model):
    id = models.AutoField(primary_key=True)
    fincode = models.IntegerField()
    invdate = models.DateTimeField(null=True, blank=True)
    mode = models.CharField(max_length=5)
    compname = models.CharField(max_length=255, null=True, blank=True)
    s_name = models.CharField(max_length=150, null=True, blank=True)
    mktval = models.FloatField(null=True, blank=True)
    noshares = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_portfolio_inout"
        verbose_name = "MF Portfolio InOut"
        verbose_name_plural = "MF Portfolio InOuts"
        unique_together = (('fincode', 'invdate', 'mode'),)

class MFAverageSchemeAUM(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    date = models.DateTimeField(null=True, blank=True)
    exfof = models.FloatField(null=True, blank=True)
    fof = models.FloatField(null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_average_scheme_aum"
        verbose_name = "MF Average Scheme AUM"
        verbose_name_plural = "MF Average Scheme AUMs"
        unique_together = (('schemecode', 'date'),)


# 1.2 NET ASSET VALUE

class MFNSEAssetValueLatest(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    navdate = models.DateTimeField(null=True, blank=True)
    navrs = models.FloatField(null=True, blank=True)
    repurprice = models.FloatField(null=True, blank=True)
    saleprice = models.FloatField(null=True, blank=True)
    cldate = models.DateTimeField(null=True, blank=True)
    change = models.FloatField(null=True, blank=True)
    netchange = models.FloatField(null=True, blank=True)
    prevnav = models.FloatField(null=True, blank=True)
    prenavdate = models.DateTimeField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_nse_asset_value_latest"
        verbose_name = "MF NSE Asset Value Latest"
        verbose_name_plural = "MF NSE Asset Value Latest"

class MFNetAssetValueHistorical(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField(null=True,blank=True)
    navdate = models.DateTimeField(null=True, blank=True)
    navrs = models.FloatField(null=True, blank=True)
    repurprice = models.FloatField(null=True, blank=True)
    saleprice = models.FloatField(null=True, blank=True)
    adjustednav_c = models.FloatField(null=True, blank=True)
    adjustednav_nonc = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_net_asset_value_historical"
        verbose_name = "MF Net Asset Value Historical"
        verbose_name_plural = "MF Net Asset Value Historical"
        unique_together = (('schemecode', 'navdate'),)

class MFNetAssetValueHighLow(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    _3monthhhigh = models.FloatField(null=True, blank=True)
    _3monthlow = models.FloatField(null=True, blank=True)
    _3mhdate = models.DateTimeField(null=True, blank=True)
    _3mldate = models.DateTimeField(null=True, blank=True)
    _6monthhhigh = models.FloatField(null=True, blank=True)
    _6monthlow = models.FloatField(null=True, blank=True)
    _6mhdate = models.DateTimeField(null=True, blank=True)
    _6mldate = models.DateTimeField(null=True, blank=True)
    _9monthhhigh = models.FloatField(null=True, blank=True)
    _9monthlow = models.FloatField(null=True, blank=True)
    _9mhdate = models.DateTimeField(null=True, blank=True)
    _9mldate = models.DateTimeField(null=True, blank=True)
    _52weekhhigh = models.FloatField(null=True, blank=True)
    _52weeklow = models.FloatField(null=True, blank=True)
    _52whdate = models.DateTimeField(null=True, blank=True)
    _52wldate = models.DateTimeField(null=True, blank=True)
    _1yrhigh = models.FloatField(null=True, blank=True)
    _1yrlow = models.FloatField(null=True, blank=True)
    _1yhdate = models.DateTimeField(null=True, blank=True)
    _1yldate = models.DateTimeField(null=True, blank=True)
    _2yrhigh = models.FloatField(null=True, blank=True)
    _2yrlow = models.FloatField(null=True, blank=True)
    _2yhdate = models.DateTimeField(null=True, blank=True)
    _2yldate = models.DateTimeField(null=True, blank=True)
    _3yrhigh = models.FloatField(null=True, blank=True)
    _3yrlow = models.FloatField(null=True, blank=True)
    _3yhdate = models.DateTimeField(null=True, blank=True)
    _3yldate = models.DateTimeField(null=True, blank=True)
    _5yrhigh = models.FloatField(null=True, blank=True)
    _5yrlow = models.FloatField(null=True, blank=True)
    _5yhdate = models.DateTimeField(null=True, blank=True)
    _5yldate = models.DateTimeField(null=True, blank=True)
    ytdhigh = models.FloatField(null=True, blank=True)
    ytdlow = models.FloatField(null=True, blank=True)
    ytdhdate = models.DateTimeField(null=True, blank=True)
    ytdldate = models.DateTimeField(null=True, blank=True)
    sihigh = models.FloatField(null=True, blank=True)
    siLow = models.FloatField(null=True, blank=True)
    sihdate = models.DateTimeField(null=True, blank=True)
    sildate = models.DateTimeField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = "mf_net_asset_value_high_low"
        verbose_name = "MF Net Asset Value High Low"
        verbose_name_plural = "MF Net Asset Value High Low"


# 1.3 RETURNS

class MFReturn(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    c_date = models.DateTimeField(null=True, blank=True)
    p_date = models.DateTimeField(null=True, blank=True)
    c_nav = models.FloatField(null=True, blank=True)
    p_nav = models.FloatField(null=True, blank=True)
    _1dayret = models.FloatField(null=True, blank=True)
    _1weekdate = models.DateTimeField(null=True, blank=True)
    _1weeknav = models.FloatField(null=True, blank=True)
    _1weekret = models.FloatField(null=True, blank=True)
    _1mthdate = models.DateTimeField(null=True, blank=True)
    _1mthnav = models.FloatField(null=True, blank=True)
    _1monthret = models.FloatField(null=True, blank=True)
    _3mthdate = models.DateTimeField(null=True, blank=True)
    _3mthnav = models.FloatField(null=True, blank=True)
    _3monthret = models.FloatField(null=True, blank=True)
    _6mntdate = models.DateTimeField(null=True, blank=True)
    _6mnthnav = models.FloatField(null=True, blank=True)
    _6monthret = models.FloatField(null=True, blank=True)
    _9mnthdate = models.DateTimeField(null=True, blank=True)
    _9mnthnav = models.FloatField(null=True, blank=True)
    _9mnthret = models.FloatField(null=True, blank=True)
    _1yrdate = models.DateTimeField(null=True, blank=True)
    _1yrnav = models.FloatField(null=True, blank=True)
    _1yrret = models.FloatField(null=True, blank=True)
    _2yrdate = models.DateTimeField(null=True, blank=True)
    _2yrnav = models.FloatField(null=True, blank=True)
    _2yearret = models.FloatField(null=True, blank=True)
    _3yrdate = models.DateTimeField(null=True, blank=True)
    _3yrnav = models.FloatField(null=True, blank=True)
    _3yearret = models.FloatField(null=True, blank=True)
    _4yrdate = models.DateTimeField(null=True, blank=True)
    _4yrnav = models.FloatField(null=True, blank=True)
    _4yearret = models.FloatField(null=True, blank=True)
    _5yrdate = models.DateTimeField(null=True, blank=True)
    _5yrnav = models.FloatField(null=True, blank=True)
    _5yearret = models.FloatField(null=True, blank=True)
    incdate = models.DateTimeField(null=True, blank=True)
    incnav = models.FloatField(null=True, blank=True)
    incret = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_return"
        verbose_name = "MF Return"
        verbose_name_plural = "MF Returns"

class MFAbsoluteReturn(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    c_date = models.DateTimeField(null=True, blank=True)
    p_date = models.DateTimeField(null=True, blank=True)
    c_nav = models.FloatField(null=True, blank=True)
    p_nav = models.FloatField(null=True, blank=True)
    _1dayret = models.FloatField(null=True, blank=True)
    _1weekdate = models.DateTimeField(null=True, blank=True)
    _1weeknav = models.FloatField(null=True, blank=True)
    _1weekret = models.FloatField(null=True, blank=True)
    _1mthdate = models.DateTimeField(null=True, blank=True)
    _1mthnav = models.FloatField(null=True, blank=True)
    _1monthret = models.FloatField(null=True, blank=True)
    _3mthdate = models.DateTimeField(null=True, blank=True)
    _3mthnav = models.FloatField(null=True, blank=True)
    _3monthret = models.FloatField(null=True, blank=True)
    _6mntdate = models.DateTimeField(null=True, blank=True)
    _6mnthnav = models.FloatField(null=True, blank=True)
    _6monthret = models.FloatField(null=True, blank=True)
    _9mnthdate = models.DateTimeField(null=True, blank=True)
    _9mnthnav = models.FloatField(null=True, blank=True)
    _9mnthret = models.FloatField(null=True, blank=True)
    _1yrdate = models.DateTimeField(null=True, blank=True)
    _1yrnav = models.FloatField(null=True, blank=True)
    _1yrret = models.FloatField(null=True, blank=True)
    _2yrdate = models.DateTimeField(null=True, blank=True)
    _2yrnav = models.FloatField(null=True, blank=True)
    _2yearret = models.FloatField(null=True, blank=True)
    _3yrdate = models.DateTimeField(null=True, blank=True)
    _3yrnav = models.FloatField(null=True, blank=True)
    _3yearret = models.FloatField(null=True, blank=True)
    _4yrdate = models.DateTimeField(null=True, blank=True)
    _4yrnav = models.FloatField(null=True, blank=True)
    _4yearret = models.FloatField(null=True, blank=True)
    _5yrdate = models.DateTimeField(null=True, blank=True)
    _5yrnav = models.FloatField(null=True, blank=True)
    _5yearret = models.FloatField(null=True, blank=True)
    incdate = models.DateTimeField(null=True, blank=True)
    incnav = models.FloatField(null=True, blank=True)
    incret = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_absolute_return"
        verbose_name = "MF Absolute Return"
        verbose_name_plural = "MF Absolute Returns"

class MFAnnualizedReturn(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    c_date = models.DateTimeField(null=True, blank=True)
    p_date = models.DateTimeField(null=True, blank=True)
    c_nav = models.FloatField(null=True, blank=True)
    p_nav = models.FloatField(null=True, blank=True)
    _1dayret = models.FloatField(null=True, blank=True)
    _1weekdate = models.DateTimeField(null=True, blank=True)
    _1weeknav = models.FloatField(null=True, blank=True)
    _1weekret = models.FloatField(null=True, blank=True)
    _1mthdate = models.DateTimeField(null=True, blank=True)
    _1mthnav = models.FloatField(null=True, blank=True)
    _1monthret = models.FloatField(null=True, blank=True)
    _3mthdate = models.DateTimeField(null=True, blank=True)
    _3mthnav = models.FloatField(null=True, blank=True)
    _3monthret = models.FloatField(null=True, blank=True)
    _6mntdate = models.DateTimeField(null=True, blank=True)
    _6mnthnav = models.FloatField(null=True, blank=True)
    _6monthret = models.FloatField(null=True, blank=True)
    _9mnthdate = models.DateTimeField(null=True, blank=True)
    _9mnthnav = models.FloatField(null=True, blank=True)
    _9mnthret = models.FloatField(null=True, blank=True)
    _1yrdate = models.DateTimeField(null=True, blank=True)
    _1yrnav = models.FloatField(null=True, blank=True)
    _1yrret = models.FloatField(null=True, blank=True)
    _2yrdate = models.DateTimeField(null=True, blank=True)
    _2yrnav = models.FloatField(null=True, blank=True)
    _2yearret = models.FloatField(null=True, blank=True)
    _3yrdate = models.DateTimeField(null=True, blank=True)
    _3yrnav = models.FloatField(null=True, blank=True)
    _3yearret = models.FloatField(null=True, blank=True)
    _4yrdate = models.DateTimeField(null=True, blank=True)
    _4yrnav = models.FloatField(null=True, blank=True)
    _4yearret = models.FloatField(null=True, blank=True)
    _5yrdate = models.DateTimeField(null=True, blank=True)
    _5yrnav = models.FloatField(null=True, blank=True)
    _5yearret = models.FloatField(null=True, blank=True)
    incdate = models.DateTimeField(null=True, blank=True)
    incnav = models.FloatField(null=True, blank=True)
    incret = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_annualized_return"
        verbose_name = "MF Annualized Return"
        verbose_name_plural = "MF Annualized Returns"

class MFCAGRReturn(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    c_date = models.DateTimeField(null=True, blank=True)
    p_date = models.DateTimeField(null=True, blank=True)
    c_nav = models.FloatField(null=True, blank=True)
    p_nav = models.FloatField(null=True, blank=True)
    _1dayret = models.FloatField(null=True, blank=True)
    _1weekdate = models.DateTimeField(null=True, blank=True)
    _1weeknav = models.FloatField(null=True, blank=True)
    _1weekret = models.FloatField(null=True, blank=True)
    _1mthdate = models.DateTimeField(null=True, blank=True)
    _1mthnav = models.FloatField(null=True, blank=True)
    _1monthret = models.FloatField(null=True, blank=True)
    _3mthdate = models.DateTimeField(null=True, blank=True)
    _3mthnav = models.FloatField(null=True, blank=True)
    _3monthret = models.FloatField(null=True, blank=True)
    _6mntdate = models.DateTimeField(null=True, blank=True)
    _6mnthnav = models.FloatField(null=True, blank=True)
    _6monthret = models.FloatField(null=True, blank=True)
    _9mnthdate = models.DateTimeField(null=True, blank=True)
    _9mnthnav = models.FloatField(null=True, blank=True)
    _9mnthret = models.FloatField(null=True, blank=True)
    _1yrdate = models.DateTimeField(null=True, blank=True)
    _1yrnav = models.FloatField(null=True, blank=True)
    _1yrret = models.FloatField(null=True, blank=True)
    _2yrdate = models.DateTimeField(null=True, blank=True)
    _2yrnav = models.FloatField(null=True, blank=True)
    _2yearret = models.FloatField(null=True, blank=True)
    _3yrdate = models.DateTimeField(null=True, blank=True)
    _3yrnav = models.FloatField(null=True, blank=True)
    _3yearret = models.FloatField(null=True, blank=True)
    _4yrdate = models.DateTimeField(null=True, blank=True)
    _4yrnav = models.FloatField(null=True, blank=True)
    _4yearret = models.FloatField(null=True, blank=True)
    _5yrdate = models.DateTimeField(null=True, blank=True)
    _5yrnav = models.FloatField(null=True, blank=True)
    _5yearret = models.FloatField(null=True, blank=True)
    incdate = models.DateTimeField(null=True, blank=True)
    incnav = models.FloatField(null=True, blank=True)
    incret = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_cagr_return"
        verbose_name = "MF CAGR Return"
        verbose_name_plural = "MF CAGR Returns"

class MFCategoryWiseReturn(models.Model):
    id = models.AutoField(primary_key=True)
    classcode = models.IntegerField(null=True, blank=True)
    classname = models.CharField(max_length=500)
    opt_code = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    _1dayret = models.FloatField(null=True, blank=True)
    _1weekret = models.FloatField(null=True, blank=True)
    _2weekret = models.FloatField(null=True, blank=True)
    _3weekret = models.FloatField(null=True, blank=True)
    _1monthret = models.FloatField(null=True, blank=True)
    _2monthret = models.FloatField(null=True, blank=True)
    _3monthret = models.FloatField(null=True, blank=True)
    _6monthret = models.FloatField(null=True, blank=True)
    _9mnthret = models.FloatField(null=True, blank=True)
    _1yearret = models.FloatField(null=True, blank=True)
    _2yearret = models.FloatField(null=True, blank=True)
    _3yearret = models.FloatField(null=True, blank=True)
    _4yearret = models.FloatField(null=True, blank=True)
    _5yearret = models.FloatField(null=True, blank=True)
    incret = models.FloatField(null=True, blank=True)
    ytdret = models.FloatField(null=True, blank=True)
    _1wschemecode = models.IntegerField(null=True, blank=True)
    weekHighRet = models.FloatField(null=True, blank=True)
    _1mschemecode = models.IntegerField(null=True, blank=True)
    monthhighret = models.FloatField(null=True, blank=True)
    _3mschemecode = models.IntegerField(null=True, blank=True)
    _3monthHighret = models.FloatField(null=True, blank=True)
    _6mschemecode = models.IntegerField(null=True, blank=True)
    _6monthhighret = models.FloatField(null=True, blank=True)
    _1yschemecode = models.IntegerField(null=True, blank=True)
    _1yhighret = models.FloatField(null=True, blank=True)
    _3yschemecode = models.IntegerField(null=True, blank=True)
    _3yhighret = models.FloatField(null=True, blank=True)
    _5yschemecode = models.IntegerField(null=True, blank=True)
    _5yhighret = models.FloatField(null=True, blank=True)
    incretschemecode = models.IntegerField(null=True, blank=True)
    increthighret = models.FloatField(null=True, blank=True)
    worst1wSchemecode = models.IntegerField(null=True, blank=True)
    weekWorstRet = models.FloatField(null=True, blank=True)
    worst1mschemecode = models.IntegerField(null=True, blank=True)
    monthworstret = models.FloatField(null=True, blank=True)
    worst3mschemecode = models.IntegerField(null=True, blank=True)
    _3monthworstret = models.FloatField(null=True, blank=True)
    worst6mschemecode = models.IntegerField(null=True, blank=True)
    _6monthWorstRet = models.FloatField(null=True, blank=True)
    worst1yschemecode = models.IntegerField(null=True, blank=True)
    _1yworstret = models.FloatField(null=True, blank=True)
    worst3yschemecode = models.IntegerField(null=True, blank=True)
    _3yworstret = models.FloatField(null=True, blank=True)
    worst5yschemecode = models.IntegerField(null=True, blank=True)
    _5yworstret = models.FloatField(null=True, blank=True)
    Worstincretschemecode = models.IntegerField(null=True, blank=True)
    incretworstret = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_category_wise_return"
        verbose_name = "MF Category Wise Return"
        verbose_name_plural = "MF Category Wise Returns"
        unique_together = (('classcode', 'opt_code'),)

class MFBenchmarkIndicesAbsoluteReturn(models.Model):
    id = models.AutoField(primary_key=True)
    index_code = models.IntegerField()
    symbol = models.CharField(max_length=255, null=True, blank=True)
    scripcode = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    prev_date = models.DateTimeField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    prev_close = models.FloatField(null=True, blank=True)
    _1dayret = models.FloatField(null=True, blank=True)
    _1weekdate = models.DateTimeField(null=True, blank=True)
    _1weekclose = models.FloatField(null=True, blank=True)
    _1weekret = models.FloatField(null=True, blank=True)
    _1mthdate = models.DateTimeField(null=True, blank=True)
    _1mthclose = models.FloatField(null=True, blank=True)
    _1monthret = models.FloatField(null=True, blank=True)
    _3mthdate = models.DateTimeField(null=True, blank=True)
    _3mthclose = models.FloatField(null=True, blank=True)
    _3monthret = models.FloatField(null=True, blank=True)
    _6mntdate = models.DateTimeField(null=True, blank=True)
    _6mnthclose = models.FloatField(null=True, blank=True)
    _6monthret = models.FloatField(null=True, blank=True)
    _9mnthdate = models.DateTimeField(null=True, blank=True)
    _9mnthclose = models.FloatField(null=True, blank=True)
    _9mnthret = models.FloatField(null=True, blank=True)
    _1yrdate = models.DateTimeField(null=True, blank=True)
    _1yrclose = models.FloatField(null=True, blank=True)
    _1yrret = models.FloatField(null=True, blank=True)
    _2yrdate = models.DateTimeField(null=True, blank=True)
    _2yrclose = models.FloatField(null=True, blank=True)
    _2yearret = models.FloatField(null=True, blank=True)
    _3yrdate = models.DateTimeField(null=True, blank=True)
    _3yrclose = models.FloatField(null=True, blank=True)
    _3yearret = models.FloatField(null=True, blank=True)
    _4yrdate = models.DateTimeField(null=True, blank=True)
    _4yrclose = models.FloatField(null=True, blank=True)
    _4yearret = models.FloatField(null=True, blank=True)
    _5yrdate = models.DateTimeField(null=True, blank=True)
    _5yrclose = models.FloatField(null=True, blank=True)
    _5yearret = models.FloatField(null=True, blank=True)
    incdate = models.DateTimeField(null=True, blank=True)
    incclose = models.FloatField(null=True, blank=True)
    incret = models.FloatField(null=True, blank=True)
    _2weekdate = models.DateTimeField(null=True, blank=True)
    _2weekclose = models.FloatField(null=True, blank=True)
    _2weekret = models.FloatField(null=True, blank=True)
    _3weekdate = models.DateTimeField(null=True, blank=True)
    _3weekclose = models.FloatField(null=True, blank=True)
    _3weekret = models.FloatField(null=True, blank=True)
    _2mthdate = models.DateTimeField(null=True, blank=True)
    _2mthclose = models.FloatField(null=True, blank=True)
    _2monthret = models.FloatField(null=True, blank=True)
    ytddate = models.DateTimeField(null=True, blank=True)
    ytdclose = models.FloatField(null=True, blank=True)
    ytdret = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_benchmark_indices_absolute_return"
        verbose_name = "MF Benchmark Indices Absolute Return"
        verbose_name_plural = "MF Benchmark Indices Absolute Returns"

class MFBenchmarkIndicesAnnualisedReturn(models.Model):
    id = models.AutoField(primary_key=True)
    index_code = models.IntegerField()
    symbol = models.CharField(max_length=255, null=True, blank=True)
    scripcode = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    prev_date = models.DateTimeField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    prev_close = models.FloatField(null=True, blank=True)
    _1dayret = models.FloatField(null=True, blank=True)
    _1weekdate = models.DateTimeField(null=True, blank=True)
    _1weekclose = models.FloatField(null=True, blank=True)
    _1weekret = models.FloatField(null=True, blank=True)
    _1mthdate = models.DateTimeField(null=True, blank=True)
    _1mthclose = models.FloatField(null=True, blank=True)
    _1monthret = models.FloatField(null=True, blank=True)
    _3mthdate = models.DateTimeField(null=True, blank=True)
    _3mthclose = models.FloatField(null=True, blank=True)
    _3monthret = models.FloatField(null=True, blank=True)
    _6mnthdate = models.DateTimeField(null=True, blank=True)
    _6mnthclose = models.FloatField(null=True, blank=True)
    _6monthret = models.FloatField(null=True, blank=True)
    _9mnthdate = models.DateTimeField(null=True, blank=True)
    _9mnthclose = models.FloatField(null=True, blank=True)
    _9mnthret = models.FloatField(null=True, blank=True)
    _1yrdate = models.DateTimeField(null=True, blank=True)
    _1yrclose = models.FloatField(null=True, blank=True)
    _1yrret = models.FloatField(null=True, blank=True)
    _2yrdate = models.DateTimeField(null=True, blank=True)
    _2yrclose = models.FloatField(null=True, blank=True)
    _2yearret = models.FloatField(null=True, blank=True)
    _3yrdate = models.DateTimeField(null=True, blank=True)
    _3yrclose = models.FloatField(null=True, blank=True)
    _3yearret = models.FloatField(null=True, blank=True)
    _4yrdate = models.DateTimeField(null=True, blank=True)
    _4yrclose = models.FloatField(null=True, blank=True)
    _4yearret = models.FloatField(null=True, blank=True)
    _5yrdate = models.DateTimeField(null=True, blank=True)
    _5yrclose = models.FloatField(null=True, blank=True)
    _5yearret = models.FloatField(null=True, blank=True)
    incdate = models.DateTimeField(null=True, blank=True)
    incclose = models.FloatField(null=True, blank=True)
    incret = models.FloatField(null=True, blank=True)
    _2weekdate = models.DateTimeField(null=True, blank=True)
    _2weekclose = models.FloatField(null=True, blank=True)
    _2weekret = models.FloatField(null=True, blank=True)
    _3weekdate = models.DateTimeField(null=True, blank=True)
    _3weekclose = models.FloatField(null=True, blank=True)
    _3weekret = models.FloatField(null=True, blank=True)
    _2mthdate = models.DateTimeField(null=True, blank=True)
    _2mthclose = models.FloatField(null=True, blank=True)
    _2monthret = models.FloatField(null=True, blank=True)
    ytddate = models.DateTimeField(null=True, blank=True)
    ytdclose = models.FloatField(null=True, blank=True)
    ytdret = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_benchmark_indices_annualised_return"
        verbose_name = "MF Benchmark Indices Annualised Return"
        verbose_name_plural = "MF Benchmark Indices Annualised Returns"


# 1.4 RATIOS

class MFRatios1Year(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    upddate = models.DateTimeField(null=True, blank=True)
    datefrom = models.DateTimeField(null=True, blank=True)
    dateto = models.DateTimeField(null=True, blank=True)
    avg_x = models.FloatField(null=True, blank=True)
    avg_y = models.FloatField(null=True, blank=True)
    sd_x = models.FloatField(null=True, blank=True)
    sd_y = models.FloatField(null=True, blank=True)  
    semisd_x = models.FloatField(null=True, blank=True)
    semisd_y = models.FloatField(null=True, blank=True)
    beta_x = models.FloatField(null=True, blank=True)
    beta_y = models.FloatField(null=True, blank=True)
    corelation_x = models.FloatField(null=True, blank=True)
    corelation_y = models.FloatField(null=True, blank=True)
    betacor_x = models.FloatField(null=True, blank=True)
    betacor_y = models.FloatField(null=True, blank=True)
    treynor_x = models.FloatField(null=True, blank=True)
    treynor_y = models.FloatField(null=True, blank=True)
    fama_x = models.FloatField(null=True, blank=True)
    fama_y = models.FloatField(null=True, blank=True)
    sharpe_x = models.FloatField(null=True, blank=True)
    sharpe_y = models.FloatField(null=True, blank=True)
    jalpha_x = models.FloatField(null=True, blank=True)
    jalpha_y = models.FloatField(null=True, blank=True)
    sortino_x = models.FloatField(null=True, blank=True)
    sortino_y = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_ratios_1_year"
        verbose_name = "MF Ratios 1 Year"
        verbose_name_plural = "MF Ratios 1 Year"

class MFRatiosDefaultBenchmark1Year(models.Model):
    id = models.AutoField(primary_key=True)
    schemecode = models.IntegerField()
    upddate = models.DateTimeField(null=True, blank=True)
    datefrom = models.DateTimeField(null=True, blank=True)
    dateto = models.DateTimeField(null=True, blank=True)
    average = models.FloatField(null=True, blank=True)
    bmaverage = models.FloatField(null=True, blank=True)
    sd = models.FloatField(null=True, blank=True)
    bmsd = models.FloatField(null=True, blank=True)
    semisd = models.FloatField(null=True, blank=True)
    semisdii = models.FloatField(null=True, blank=True)
    beta = models.FloatField(null=True, blank=True)
    correlation = models.FloatField(null=True, blank=True)
    beta_corelation = models.FloatField(null=True, blank=True)  
    covariance = models.FloatField(null=True, blank=True)
    treynor = models.FloatField(null=True, blank=True)
    fama = models.FloatField(null=True, blank=True)
    sharpe = models.FloatField(null=True, blank=True)
    alpha = models.FloatField(null=True, blank=True)
    sortino = models.FloatField(null=True, blank=True)
    sortinoii = models.FloatField(null=True, blank=True)  
    ret_improper = models.FloatField(null=True, blank=True)
    ret_selectivity = models.FloatField(null=True, blank=True)
    down_probability = models.FloatField(null=True, blank=True)
    rsquared = models.FloatField(null=True, blank=True)
    trackingError = models.FloatField(null=True, blank=True)
    down_risk = models.FloatField(null=True, blank=True)  
    sd_annualised = models.FloatField(null=True, blank=True)  
    informationRatio = models.FloatField(null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_ratios_default_benchmark_1_year"
        verbose_name = "MF Ratios Default Benchmark 1 Year"
        verbose_name_plural = "MF Ratios Default Benchmark 1 Year"

class MFRatios3Year(models.Model):
    id = models.AutoField(primary_key=True)
    SCHEMECODE = models.IntegerField()  
    RatioDate = models.DateField(null=True, blank=True)
    Average_Nav = models.FloatField(null=True, blank=True)
    SD_Nav = models.FloatField(null=True, blank=True)
    SemiSD = models.FloatField(null=True, blank=True)
    Beta = models.FloatField(null=True, blank=True)
    Corel = models.FloatField(null=True, blank=True)
    BetaCorel = models.FloatField(null=True, blank=True)
    Rsq = models.FloatField(null=True, blank=True)
    Trey = models.FloatField(null=True, blank=True)
    Fama = models.FloatField(null=True, blank=True)
    Sharpe = models.FloatField(null=True, blank=True)
    Jalpha = models.FloatField(null=True, blank=True)
    Sortino = models.FloatField(null=True, blank=True)
    retdueimp = models.FloatField(null=True, blank=True)
    retduesel = models.FloatField(null=True, blank=True)
    downsideprob = models.FloatField(null=True, blank=True)
    downsiderisk = models.FloatField(null=True, blank=True)
    SortinoSD = models.FloatField(null=True, blank=True)
    TrackingError = models.FloatField(null=True, blank=True)
    InformationRatio = models.FloatField(null=True, blank=True)
    SDAnn = models.FloatField(null=True, blank=True)
    AvgIndex = models.FloatField(null=True, blank=True)
    SD_Index = models.FloatField(null=True, blank=True)
    CoVar = models.FloatField(null=True, blank=True)
    MaxRet = models.FloatField(null=True, blank=True)
    MinRet = models.FloatField(null=True, blank=True)
    RFR = models.FloatField(null=True, blank=True)
    PriceIndex = models.IntegerField(null=True, blank=True) 
    PriceIndexName = models.CharField(max_length=255, null=True, blank=True)
    Flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_ratios_3_year"
        verbose_name = "MF Ratios 3 Year"
        verbose_name_plural = "MF Ratios 3 Year"


# 1.5 DIVIDEND

class MFDividendDetails(models.Model):
    id = models.AutoField(primary_key=True)
    amc_code = models.IntegerField()
    schemecode = models.IntegerField()
    recorddate = models.DateTimeField(null=True, blank=True)
    div_code = models.IntegerField(null=True, blank=True)
    exdivdate = models.DateTimeField(null=True, blank=True)
    Bonusrate1 = models.FloatField(null=True, blank=True)
    Bonusrate2 = models.FloatField(null=True, blank=True)
    gross = models.FloatField(null=True, blank=True)
    corporate = models.FloatField(null=True, blank=True)
    noncorporate = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=3, null=True, blank=True)
    flag = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_dividend_details"
        verbose_name = "MF Dividend Detail"
        verbose_name_plural = "MF Dividend Details"
        unique_together = (('schemecode', 'recorddate'),)