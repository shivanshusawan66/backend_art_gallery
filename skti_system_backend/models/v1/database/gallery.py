from django.db import models

class Tag(models.Model):
    name       = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Artwork(models.Model):
    title       = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    category    = models.ForeignKey(Category, on_delete=models.PROTECT)
    image       = models.ImageField(upload_to='artworks/')
    tags        = models.ManyToManyField(Tag, related_name='artworks', blank=True)
    is_deleted  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'artworks'
        verbose_name = 'Artwork'
        verbose_name_plural = 'Artworks'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
