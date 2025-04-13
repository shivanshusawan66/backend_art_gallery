import logging
from django.db import models
from ai_mf_backend.models.v1.database import SoftDeleteModel
from ai_mf_backend.models.v1.database.questions import Section

logger = logging.getLogger(__name__)

class MFMarker(SoftDeleteModel):
    section_id = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        db_column="section_id"
    )
    marker = models.CharField(max_length=500)
    initial_marker_weight = models.FloatField(default=0.0)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mf_marker"
        verbose_name = "MF Marker"
        verbose_name_plural = "MF Markers"

    def __str__(self):
        return self.marker

class MFMarkerOptions(SoftDeleteModel):
    section_id = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        db_column="section_id"
    )
    marker_id = models.ForeignKey(
       MFMarker,
       on_delete=models.PROTECT,
       db_column="marker_id"
    )
    option = models.TextField()
    position = models.PositiveIntegerField(default=0.0)
    option_weight = models.FloatField(default=0.0)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mf_marker_options"
        verbose_name = "MF Marker Option"
        verbose_name_plural = "MF Marker Options"

    def __str__(self):
        return self.option
