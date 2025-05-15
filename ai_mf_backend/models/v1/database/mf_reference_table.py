from django.db import models

from ai_mf_backend.models.v1.database.mf_embedding_tables import MFMarker

class MFReferenceTable(models.Model):
    table_name = models.CharField(
        max_length=255,
    )
    marker_name = models.CharField(
        max_length=255,
    )
    lookup_field = models.CharField(
        max_length=255, 
        null=True, 
        blank=True
    )
    outer_ref = models.CharField(
        max_length=255, 
        null=True, 
        blank=True
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

class MFMarkerOptionsText(models.Model):
    marker_id = models.ForeignKey(
        MFMarker, on_delete=models.PROTECT, db_column="marker_id"
    )
    option = models.TextField()
    position = models.PositiveIntegerField(default=0.0)

    class Meta:
        db_table = "mf_marker_options_text"
        verbose_name = "MF Marker Option Text"
        verbose_name_plural = "MF Marker Option Texts"

    def __str__(self):
        return self.option