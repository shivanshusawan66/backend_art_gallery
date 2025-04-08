import logging

from django.db import models

from ai_mf_backend.models.v1.database import SoftDeleteModel
from ai_mf_backend.utils.v1.authentication.validators import custom_validate_international_phonenumber
from ai_mf_backend.utils.v1.validators.name import validate_name


logger = logging.getLogger(__name__)

class ContactMessageFundCategory(SoftDeleteModel):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[validate_name]
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "contact_message_fund_category"
        verbose_name = "Contact Message Fund Cateogory"
        verbose_name_plural = "Contact Message Fund Categories"

    def __str__(self):
        return self.name
    
class ContactMessage(SoftDeleteModel):
    first_name = models.CharField(
        max_length=100,
        validators=[validate_name]
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    email = models.EmailField()
    phone_number = models.CharField(
        max_length=20,
        validators=[custom_validate_international_phonenumber]
    )
    category_id = models.ForeignKey(
        ContactMessageFundCategory,
        on_delete=models.PROTECT,
        db_column="category_id",
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contact_message"
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']