from django.db import models


# Create your models here.
class Provinces(models.Model):
    '''用户模型'''
    pname = models.CharField(max_length=200, null=True, unique=True)

    def __str__(self):
        return self.pname


class Citys(models.Model):
    '''用户模型'''
    cname = models.CharField(max_length=200, null=True, unique=True)
    cprovince = models.ForeignKey(Provinces)

    def __str__(self):
        return self.cname


class Areas(models.Model):
    '''用户模型'''
    aname = models.CharField(max_length=200, null=True, unique=True)
    acity = models.ForeignKey(Citys)
    def __str__(self):
        return self.aname
