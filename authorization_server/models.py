from django.db import models


# Create your models here.
class Customer(models.Model):
    """
    A Customer is a company working with enerfrog
    """

    customer_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.customer_name


class Role(models.Model):
    """
    Roles is a list of roles that a user can have
    """

    role_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.role_name


class Platform(models.Model):
    """
    Platforms is a list of platforms that a user can have
    """

    platform_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.platform_name


class Permission(models.Model):
    """
    Permissions is a list of permissions that a user can have
    """

    permission_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.permission_name


class User(models.Model):
    """
    Main user model
    """

    # 3rd party auth id
    user_id = models.CharField(max_length=255, unique=True, null=False, blank=False)
    email = models.EmailField(max_length=255, unique=True, blank=False, null=False)
    username = models.CharField(max_length=255, null=True, blank=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    roles = models.ManyToManyField(Role, blank=True)
    platforms = models.ManyToManyField(Platform, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    metadata = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return f"{self.email} | {self.user_id}"
