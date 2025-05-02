import logging
from django.db import models
from ai_mf_backend.models.v1.database import SoftDeleteModel


logger = logging.getLogger(__name__)


class MFFilterParameters(SoftDeleteModel):
    parameter_name = models.CharField(max_length=50, unique=True)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mf_filter_parameters"
        verbose_name = "MF Filter Parameter"
        verbose_name_plural = "MF Filter Parameters"

    def __str__(self):
        return self.parameter_name


class MFFilterColors(SoftDeleteModel):
    color_name = models.CharField(max_length=50, unique=True)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mf_filter_colors"
        verbose_name = "MF Filter Color"
        verbose_name_plural = "MF Filter Colors"

    def __str__(self):
        return self.color_name
