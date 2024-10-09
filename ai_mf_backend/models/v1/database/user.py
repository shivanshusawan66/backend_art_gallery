from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
def validate_mobile_number(value):

    if value and (len(value) != 10 or not value.isdigit()):
        raise ValidationError(
            "Mobile number must be exactly 10 digits long and contain only numbers."
        )


class Gender(models.Model):
    gender = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gender"
    
    def __str__(self):
        return self.gender


class MaritalStatus(models.Model):
    status = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "marital_status"
    
    def __str__(self):
        return self.status


class Occupation(models.Model):
    occupation = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "occupation"
    
    def __str__(self):
        return self.occupation


class UserContactInfo(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True,blank=True,null=True)
    mobile_number = models.CharField(
        max_length=10, validators=[validate_mobile_number], blank=True, null=True,unique=True
    )
    password = models.CharField(max_length=100, blank=True, null=True)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_contact_info"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["mobile_number"]),
        ]

    def __str__(self):
        return self.email

class UserPersonalDetails(models.Model):
    user = models.ForeignKey(UserContactInfo, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT)
    marital_status = models.ForeignKey(MaritalStatus, on_delete=models.PROTECT)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_personal_details"
    
    def __str__(self):
        return self.name


class UserOTP(models.Model):
    user = models.ForeignKey(UserContactInfo, on_delete=models.CASCADE)
    otp = models.IntegerField()
    otp_valid = models.DateTimeField()
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_otp"
    
    def __str__(self):
        return f"OTP for {self.user.name}"