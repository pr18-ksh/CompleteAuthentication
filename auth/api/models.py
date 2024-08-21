from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=15,null=True,unique=True)
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        related_name="custom_user_set",  # Added related_name
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_set",  # Added related_name
        related_query_name="user",
    )

    class Meta:
        permissions = (("can_view_customuser", "Can view custom user"),)

    def _str_(self):
        return self.username
        # return f'{self.first_name} {self.last_name}'