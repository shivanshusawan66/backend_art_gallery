from ai_mf_backend import models

from ai_mf_backend.utils.v1.enums import ReferenceTableEnums

from ai_mf_backend.utils.v1.constants import refresh_constants


class Reference(models.Model):
    table_name = models.CharField(max_length=255)

    column_name = models.CharField(max_length=255)

    display_name = models.CharField(max_length=255)

    reference_type = models.CharField(
        max_length=255, choices=[i.value for i in ReferenceTableEnums]
    )

    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.table_name}.{self.column_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        refresh_constants()
