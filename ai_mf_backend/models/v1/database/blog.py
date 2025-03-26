from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from ai_mf_backend.models.v1.database import SoftDeleteModel
from ai_mf_backend.models.v1.database.user import UserContactInfo, UserPersonalDetails
from ai_mf_backend.utils.v1.database.filepath import generate_unique_filename
from ai_mf_backend.utils.v1.database.images import validate_image_size


class BlogCategory(SoftDeleteModel):
    name = models.CharField(max_length=50, unique=True)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_category"
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Category"

    def __str__(self):
        return self.name
    
class BlogData(SoftDeleteModel):
    id = models.AutoField(primary_key=True)
    user_id  = models.ForeignKey(
        UserContactInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        db_column='user_id'
    )
    username = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        editable=False
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    blog_description = CKEditor5Field(
        config_name='extends',
        blank=False,
        null=False
    )
    user_image = models.ImageField(
        upload_to="user_images/",
        null=True,
        blank=True,
        editable=False
    )
    blogcard_image = models.ImageField(
        upload_to='blogcard_images/',
        blank=True,
        null=True,
        validators=[validate_image_size] 
    )
    created_at = models.DateTimeField(auto_now_add=True)

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

        if self.blogcard_image:
            unique_filename = generate_unique_filename(self.blogcard_image.name)
            self.blogcard_image.name = unique_filename
        
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = "blog_data"
        verbose_name = "Blog Data"
        verbose_name_plural = "Blogs Data"
        

    def __str__(self):
        return f"{self.id} - {self.title}"

class BlogComment(SoftDeleteModel):
    user = models.ForeignKey(
        UserContactInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    blog_post = models.ForeignKey(
        BlogData,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    content = models.TextField()
    username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.username and self.user:
            try:
                user_details = UserPersonalDetails.objects.get(user=self.user)
                self.username = user_details.name
            except UserPersonalDetails.DoesNotExist:
                self.username = "Unknown User"
        super().save(*args, **kwargs)

    class Meta:
        db_table = "blog_comment"
        verbose_name = "Blog Comment"
        verbose_name_plural = "Blog Comments"

    def __str__(self):
        blog_title = self.blog_post.title if self.blog_post else "[Deleted Blog Post]"
        return f"Comment by {self.username} on {blog_title}"