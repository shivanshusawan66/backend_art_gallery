import logging
from django.db import models
from ai_mf_backend.models.v1.database import SoftDeleteModel


logger = logging.getLogger(__name__)

class MutualFundType(SoftDeleteModel):
    fund_type = models.CharField(max_length=50, unique=True)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mutual_fund_type"
        verbose_name = "Mutual Fund Type"
        verbose_name_plural = "Mutual Fund Types"

    def __str__(self):
        return self.fund_type

class MutualFundSubcategory(SoftDeleteModel):
    fund_type_id = models.ForeignKey(
        MutualFundType,
        on_delete=models.PROTECT,
        db_column="fund_type_id",
    )
    fund_subcategory = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mutual_fund_subcategory"
        verbose_name = "Mutual Fund Subcategory"
        verbose_name_plural = "Mutual Fund Subcategories"

    def __str__(self):
        return self.fund_subcategory