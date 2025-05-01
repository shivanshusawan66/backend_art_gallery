from django.db import models
from ai_mf_backend.models.v1.database import SoftDeleteModel
from ai_mf_backend.models.v1.database.user import UserContactInfo

# models.py


class PortfolioSchema(SoftDeleteModel):
    user_id = models.ForeignKey(
        UserContactInfo, on_delete=models.PROTECT, db_column="user_id"
    )

    scheme_code = models.IntegerField()
    current_fund_nav = models.FloatField()
    investment_date = models.DateField()
    investment_type = models.CharField()
    frequency = models.CharField(max_length=20, null=True, blank=True)
    invested_amount = models.FloatField()
    quantity = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=["user_id"]),
        ]
        abstract = True
    

class MFRealPortfolio(PortfolioSchema):

    class Meta:
        db_table = "mf_real_portfolio"
        verbose_name = "MFReal Portfolio"
        verbose_name_plural = "MFReal Portfolios"


class MFTrialPortfolio(PortfolioSchema):

    class Meta:
        db_table = "mf_trial_portfolio"
        verbose_name = "MFTrial Portfolio"
        verbose_name_plural = "MFTrial Portfolios"