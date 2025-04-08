from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from ai_mf_backend.models.v1.database.user import UserContactInfo, UserPersonalDetails
from ai_mf_backend.models.v1.database import SoftDeleteModel

class UserReview(SoftDeleteModel):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        UserContactInfo, on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="user_id",
    )
    username = models.CharField(max_length=100, blank=True, null=True, editable=False)
    designation = models.CharField(max_length=100, blank=True, null=True)
    review_title = models.CharField(max_length=100, blank=False, null=False)
    review_body = models.TextField(blank=False, null=False)
    number_of_stars = models.IntegerField(blank=False, null=False, validators=[MinValueValidator(0), MaxValueValidator(5)])
    location = models.CharField(max_length=100, blank=True, null=True)
    user_image = models.ImageField(
        null=True,
        blank=True,
        editable=False
    )
    add_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.user_id:
            try:
                user_details = (
                UserPersonalDetails.objects.filter(user=self.user_id)
                .order_by('-add_date') 
                .first()
            )
            except UserPersonalDetails.DoesNotExist:
                user_details = None

            if not self.username:
                self.username = user_details.name if user_details else "Unknown User"

            if not self.user_image:
                self.user_image = user_details.user_image if user_details else None
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = "user_review"
        verbose_name = "User Review"
        verbose_name_plural = "User Reviews"

    def __str__(self):
        return f"{self.id} - {self.review_title}"