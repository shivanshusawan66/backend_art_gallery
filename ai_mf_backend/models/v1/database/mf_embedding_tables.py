from django.db import models
import logging
from ai_mf_backend.models.v1.database import SoftDeleteModel
from ai_mf_backend.models.v1.database.questions import Section

logger = logging.getLogger(__name__)


class MFMarker(SoftDeleteModel):
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT
    )
    Marker = models.CharField(max_length=500)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    initial_Marker_weight = models.FloatField(default=0.0)

    class Meta:
        db_table = "question"
        verbose_name = "Question"
        verbose_name_plural = "Question"

    def __str__(self):
        return self.Marker


class MFMarkerOptions(SoftDeleteModel):
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT
    )
    Marker = models.ForeignKey(
       MFMarker, on_delete=models.PROTECT
    )
    option = models.CharField(max_length=500)
    position = models.PositiveIntegerField(default=0.0)
    option_weight = models.FloatField(default=0.0)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "allowed_response"
        verbose_name = "Allowed Response"
        verbose_name_plural = "Allowed Response"

    def __str__(self):
        return self.option

class MutualFundResponse(SoftDeleteModel):
    scheme_code = models.IntegerField()
    marker = models.ForeignKey(
        MFMarker, on_delete=models.PROTECT
    )
    Option = models.ForeignKey(
        MFMarkerOptions, on_delete=models.PROTECT
    )
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_response"
        verbose_name = "User Response"
        verbose_name_plural = "User Response"

    def __str__(self):
        return f"{self.scheme_code} - {self.marker}"
    

class MarkerWeightsPerMutualFund(SoftDeleteModel):
    scheme_code = models.IntegerField()
    marker = models.ForeignKey(
        MFMarker, on_delete=models.PROTECT
    )
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT
    )
    weight = models.FloatField(default=0.0)


class SectionWeightsPerMutualFund(SoftDeleteModel):
    scheme_code = models.IntegerField()
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT
    )
    weight = models.FloatField(default=0.0)
