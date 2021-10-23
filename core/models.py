from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from .storages_backends import Logos
from uuid import uuid4

ACCESS_CHOICES = [("ALL", "ALL"), ("RESTRICTED", "RESTRICTED")]
CATEGORY_CHOICES = [("Retail", "Retail"), ("Warehouse", "Warehouse")]


class Customer(models.Model):
    """
    A Customer is a company working with enerfrog
    """

    customer_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.customer_name


class UserInfo(models.Model):
    """
    User info will handle all the permissions for the user
    NB: username here is the id on auth0
    """

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        db_column="user",
        null=True,
        to_field="username",
        related_name="user_info",
    )

    # Storing a user name here
    user_name = models.CharField(max_length=255, unique=True, null=False, blank=False)

    access_level = models.CharField(
        max_length=10,
        default="RESTRICTED",
        blank=False,
        null=False,
        choices=ACCESS_CHOICES,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        db_column="customer",
        null=True,
        blank=True,
        to_field="customer_name",
    )

    # Access to division level stats
    access_division_energy = models.BooleanField(default=False, null=False, blank=False)

    # Access to division level project stats
    access_division_project = models.BooleanField(
        default=False, null=False, blank=False
    )

    # Access to facility level energy
    access_facility_energy = models.BooleanField(default=False, null=False, blank=False)

    # Access to facility level project
    access_facility_project = models.BooleanField(
        default=False, null=False, blank=False
    )

    # Access to investigations
    access_investigation = models.BooleanField(default=False, null=False, blank=False)

    # Allow to address investigations
    is_investigator = models.BooleanField(default=True, null=False, blank=False)

    # Allow to approve and create investigations
    is_investigation_manager = models.BooleanField(
        default=False,
        blank=False,
    )

    # User are only confirmed once manually validated
    confirmed_user = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = "User Info"

    def __str__(self):
        return f"Status for: {self.user}"


class Division(models.Model):
    """
    A category within a customer's organization
    will be used to aggregate results
    """

    division_name = models.CharField(
        max_length=50, null=False, blank=False, unique=True
    )
    logo = models.FileField(storage=Logos(), null=True, blank=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        db_column="customer",
        null=True,
        blank=True,
        to_field="customer_name",
    )

    class Meta:
        verbose_name_plural = "Divisions"

    def __str__(self):
        return f"{self.division_name}"


class Facility(models.Model):
    """
    Model for facilities
    """

    division = models.ForeignKey(
        Division,
        to_field="division_name",
        null=True,
        on_delete=models.SET_NULL,
        related_name="facility_to_division",
        db_column="division",
    )
    # The facility name is used for the system as well non modifiable foreign key
    facility_name = models.CharField(
        max_length=50, null=False, blank=False, unique=True
    )
    # An identifier is simply a name given to the facility and can be null
    facility_identifier = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=20, decimal_places=7, null=False, blank=False, default=0.0
    )
    longitude = models.DecimalField(
        max_digits=20, decimal_places=7, null=False, blank=False, default=0.0
    )
    area = models.IntegerField(
        null=True, blank=True, default=1, validators=[MinValueValidator(1)]
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    category_type = models.CharField(
        max_length=15,
        choices=CATEGORY_CHOICES,
        default="Retail",
        null=False,
        blank=False,
    )
    closed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Facilities"

    def __str__(self):
        return f"{self.facility_name}"


class FacilityAccessControl(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user",
        null=True,
        to_field="username",
        related_name="facility_access_control",
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        db_column="facility",
        null=True,
        blank=True,
        to_field="facility_name",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "facility"], name="NoDup_user_facility"
            )
        ]

    def __str__(self):
        return "{} - {}".format(self.user, self.facility)
