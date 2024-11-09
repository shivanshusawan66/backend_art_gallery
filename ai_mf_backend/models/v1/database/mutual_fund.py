from django.db import models
from django.utils import timezone


class MutualFund(models.Model):
    scheme_name = models.CharField(max_length=255, unique=True)
    q_param = models.CharField(max_length=100)
    net_asset_value = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    date = models.DateField()
    symbol = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.scheme_name


class FundOverview(models.Model):
    fund = models.OneToOneField(
        MutualFund, on_delete=models.CASCADE, related_name="overview"
    )
    category = models.CharField(max_length=100, null=True, blank=True)
    fund_family = models.CharField(max_length=255, null=True, blank=True)
    net_assets = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    ytd_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    yield_value = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    morningstar_rating = models.CharField(max_length=10, null=True, blank=True)
    inception_date = models.DateField(null=True, blank=True)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


class HistoricalData(models.Model):
    fund = models.ForeignKey(
        MutualFund, on_delete=models.CASCADE, related_name="historical_data"
    )
    date = models.DateTimeField()
    open = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    high = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    low = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    close = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    adj_close = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    volume = models.BigIntegerField(default=0)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("fund", "date")


class PerformanceData(models.Model):
    fund = models.OneToOneField(
        MutualFund, on_delete=models.CASCADE, related_name="performance_data"
    )
    morningstar_return_rating = models.CharField(max_length=10, null=True, blank=True)
    ytd_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    average_return_5y = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    number_of_years_up = models.IntegerField(null=True, default=0)
    number_of_years_down = models.IntegerField(null=True, default=0)
    best_1y_total_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    worst_1y_total_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    best_3y_total_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    worst_3y_total_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


class TrailingReturn(models.Model):
    fund = models.ForeignKey(
        MutualFund, on_delete=models.CASCADE, related_name="trailing_returns"
    )
    metric = models.CharField(max_length=50)
    fund_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    benchmark_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


class AnnualReturn(models.Model):
    fund = models.ForeignKey(
        MutualFund, on_delete=models.CASCADE, related_name="annual_returns"
    )
    year = models.IntegerField()
    fund_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    category_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


class FundData(models.Model):
    fund = models.OneToOneField(
        MutualFund, on_delete=models.CASCADE, related_name="fund_data"
    )
    min_initial_investment = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0.00
    )
    min_subsequent_investment = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0.00
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


class RiskStatistics(models.Model):
    fund = models.ForeignKey(
        MutualFund, on_delete=models.CASCADE, related_name="risk_statistics"
    )
    period = models.CharField(max_length=10)
    alpha = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0.00)
    beta = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0.00)
    mean_annual_return = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    r_squared = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    standard_deviation = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    sharpe_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    treynor_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=0.00
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("fund", "period")


class AMFIMutualFund(models.Model):
    scheme_name = models.CharField(max_length=255, unique=True)
    q_param = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.scheme_name
