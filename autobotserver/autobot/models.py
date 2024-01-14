from django.db import models
from django.contrib.postgres.fields import ArrayField


class Applicant(models.Model):
    telegram_name = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, unique=True)
    name_from_user = models.CharField(max_length=100, null=True)
    telephone_number = models.CharField(max_length=100, null=True)
    urls = ArrayField(models.CharField(max_length=200))
    request = models.BooleanField(default=False)

# class Event(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     price_for_new = models.IntegerField()
#     price_for_old = models.IntegerField()
#     event_photo_id = models.CharField(max_length=100)
#     ticket_photo_id = models.CharField(max_length=100)
#     description = models.TextField()
#     event_date = models.DateField(null=True, max_length=100)
