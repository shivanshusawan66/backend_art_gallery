from django.db import models
import logging
from django.core.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from ai_mf_backend.models.v1.database import SoftDeleteModel
from ai_mf_backend.utils.v1.database.filepath import generate_unique_filename
from ai_mf_backend.utils.v1.database.images import validate_image_size
from ai_mf_backend.utils.v1.validators.dates import (
    validate_not_future_date,
    validate_reasonable_birth_date,
)
from ai_mf_backend.utils.v1.validators.name import validate_name
from ai_mf_backend.utils.v1.validators.status import (
    validate_marital_status,
    validate_gender,
    validate_occupation,
)

logger = logging.getLogger(__name__)


def validate_mobile_number(mobile_no: str) -> None:

    # We expect phone number in the format of +91 8473829478
    try:
        _ = validate_international_phonenumber(mobile_no)
    except ValidationError:
        raise ValidationError(
            "Mobile number must be exactly 10 digits long and contain only numbers."
        )


class Gender(SoftDeleteModel):
    gender = models.CharField(max_length=50, unique=True, validators=[validate_gender])
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gender"
        verbose_name = "Gender"
        verbose_name_plural = "Gender"

    def __str__(self):
        return self.gender


class MaritalStatus(SoftDeleteModel):

    marital_status = models.CharField(
        max_length=50, unique=True, validators=[validate_marital_status]
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "marital_status"
        verbose_name = "Marital Status"
        verbose_name_plural = "Marital Status"

    def __str__(self):
        return self.marital_status


class Occupation(SoftDeleteModel):
    occupation = models.CharField(
        max_length=100, unique=True, validators=[validate_occupation]
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "occupation"
        verbose_name = "Occupation"
        verbose_name_plural = "Occupation"

    def __str__(self):
        return self.occupation


class UserContactInfo(SoftDeleteModel):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    mobile_number = models.CharField(
        validators=[validate_mobile_number], blank=True, null=True, unique=True
    )
    password = models.CharField(max_length=100, blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    questionnaire_filled = models.BooleanField(default=False)

    user_details_filled = models.BooleanField(default=False)

    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.mobile_number == "":
            self.mobile_number = None
        if self.email == "":
            self.email = None
        super(UserContactInfo, self).save(*args, **kwargs)

    class Meta:
        db_table = "user_contact_info"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["mobile_number"]),
        ]
        verbose_name = "User Contact Info"
        verbose_name_plural = "User Contact Info"

    def __str__(self):
        return self.email or self.mobile_number or "Unknown User"


class UserPersonalDetails(SoftDeleteModel):
    user = models.ForeignKey(
        UserContactInfo, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(
        max_length=100, null=True, blank=True, validators=[validate_name]
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        validators=[validate_reasonable_birth_date, validate_not_future_date],
    )
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    marital_status = models.ForeignKey(
        MaritalStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    user_image = models.ImageField(
        upload_to='user_images/',
        blank=True,
        null=True,
        validators=[validate_image_size]
    )
    add_date = models.DateTimeField(
        auto_now_add=True, validators=[validate_not_future_date]
    )
    update_date = models.DateTimeField(
        auto_now=True, validators=[validate_not_future_date]
    )

    def save(self, *args, **kwargs):
        if self.user_image:
            unique_filename = generate_unique_filename(self.user_image.name)
            self.user_image.name = unique_filename
        super().save(*args, **kwargs)

    class Meta:
        db_table = "user_personal_details"

    def __str__(self):
        return f"Personal Details for {self.user}"
    

class OTPlogs(SoftDeleteModel):
    user = models.ForeignKey(
        UserContactInfo, on_delete=models.SET_NULL, null=True, blank=True
    )
    otp = models.IntegerField(null=False, blank=False)
    otp_valid = models.DateTimeField(null=False, blank=False)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "otp_logs"
        verbose_name = "OTP Logs"
        verbose_name_plural = "OTP Logs"

    def __str__(self):
        return f"OTP for {self.user}"
