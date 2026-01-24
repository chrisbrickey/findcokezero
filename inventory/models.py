from django.db import models


class Soda(models.Model):

    name = models.CharField(max_length=100, blank=False, unique=True)
    abbreviation = models.CharField(max_length=2, blank=False, unique=True)
    low_calorie = models.BooleanField(default=False)

    # declares a field to display on the Django admin or anytime you want string representation of the entire object; must be unique
    def __str__(self) -> str:
        return self.name


class Retailer(models.Model):

    name = models.CharField(max_length=100, blank=False, unique=True)
    street_address = models.CharField(max_length=200, blank=False, unique=True)
    city = models.CharField(max_length=100, blank=False)
    postcode = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    timestamp_last_updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp_created = models.DateTimeField(auto_now=False, auto_now_add=True)

    sodas = models.ManyToManyField(Soda, blank=True)

    # declares a field to display on the Django admin or anytime you want string representation of the entire object; must be unique
    def __str__(self) -> str:
        return self.name
