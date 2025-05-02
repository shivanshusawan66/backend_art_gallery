from django.db import models


class MFReferenceTable(models.Model):
    table_name = models.CharField(
        max_length=255,
    )
    marker_name = models.CharField(
        max_length=255,
    )
    display_name = models.CharField(
        max_length=255,
    )
    add_date = models.DateTimeField(
        auto_now_add=True,
    )
    update_date = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "mf_reference_table"
        verbose_name = "MF Reference Table"
        verbose_name_plural = "MF Reference Table"
        unique_together = [["table_name", "marker_name"]]

    def __str__(self):
        return f"{self.table_name}.{self.marker_name}"
