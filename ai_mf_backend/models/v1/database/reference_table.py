from django.db import models
from ai_mf_backend.utils.v1.enums import ReferenceTableEnums
from datetime import datetime


class Reference(models.Model):
    """
    Stores table-column mappings for API projections.
    """

    table_name = models.CharField(max_length=255, verbose_name="Table Name")
    column_name = models.CharField(max_length=255, verbose_name="Markers Name")
    display_name = models.CharField(max_length=255, verbose_name="Display Name")
    add_date = models.DateTimeField(auto_now_add=True, verbose_name="Date Added")
    update_date = models.DateTimeField(auto_now=True, verbose_name="Date Updated")

    class Meta:
        unique_together = [["table_name", "column_name"]]
        verbose_name = "Reference"
        verbose_name_plural = "References"

    def __str__(self):
        return f"{self.table_name}.{self.column_name}"
