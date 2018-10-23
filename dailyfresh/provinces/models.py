from django.db import models
# from  django.contrib.auth.models import AbstractUser
# from db.base_model import BaseModel


class Testappf(models.Model):
    add = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'testappf'
