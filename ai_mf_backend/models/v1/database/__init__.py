from django.db import models

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        """Return only objects that are not soft deleted."""
        return super().get_queryset().filter(deleted=False)

    def all_with_deleted(self):
        """Return all objects, including soft deleted ones."""
        return super().get_queryset()

class SoftDeleteModel(models.Model):
    deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()  # Use the custom manager by default

    def delete(self, *args, **kwargs):
        """Soft delete the object by setting deleted to True."""
        self.deleted = True
        self.save()

    def restore(self, *args, **kwargs):
        """Restore the object by setting deleted to False."""
        self.deleted = False
        self.save()

    def hard_delete(self, *args, **kwargs):
        """Permanently delete the object from the database."""
        super(SoftDeleteModel, self).delete(*args, **kwargs)

    class Meta:
        abstract = True
