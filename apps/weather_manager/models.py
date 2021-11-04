from django.db import models


class WeatherStation(models.Model):
    pk_id = models.AutoField(db_column="pk", primary_key=True)
    climate_id = models.CharField(unique=True, max_length=255)
    station_name = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        managed = False
        db_table = "weatherstation"


class WeatherData(models.Model):
    pk_id = models.AutoField(db_column="pk", primary_key=True)
    climate_id = models.ForeignKey(
        WeatherStation,
        db_column="climate_id",
        to_field="climate_id",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    date = models.DateField()
    hdd = models.FloatField()
    cdd = models.FloatField()

    def __str__(self):
        return f"climate_id: {self.climate_id_id} - date: {self.date}"

    class Meta:
        managed = False
        db_table = "weatherdata"
        unique_together = (("climate_id", "date"),)
