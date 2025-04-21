import logging
from django.db import models
from pgvector.django import VectorField
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
    
class MFResponse(SoftDeleteModel):
    scheme_code = models.IntegerField()
    marker_id = models.ForeignKey(
        MFMarker,
        on_delete=models.PROTECT,
        db_column="marker_id"
    )
    option_id = models.ForeignKey(
        MFMarkerOptions,
        on_delete=models.PROTECT,
        db_column="option_id"
    )
    section_id = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        db_column="section_id"
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mf_response"
        verbose_name = "MF Response"
        verbose_name_plural = "MF Response"

    def __str__(self):
        return f"{self.scheme_code} - {self.marker_id}"
    

class MarkerWeightsPerMutualFund(SoftDeleteModel):
    scheme_code = models.IntegerField()
    marker = models.ForeignKey(
        MFMarker, on_delete=models.PROTECT
    )
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT
    )
    weight = models.FloatField(default=0.0)

    class Meta:
        db_table = "marker_weights_per_mutual_fund"
        verbose_name = "Marker Weights Per Mutual Fund"
        verbose_name_plural = "Marker Weights Per Mutual Fund"

class SectionWeightsPerMutualFund(SoftDeleteModel):
    scheme_code = models.IntegerField()
    embedding = VectorField(dimensions=7)

    class Meta:
        db_table = "section_weights_per_mutual_fund"
        verbose_name = "Section Weights Per Mutual Fund"
        verbose_name_plural = "Section Weights Per Mutual Fund"