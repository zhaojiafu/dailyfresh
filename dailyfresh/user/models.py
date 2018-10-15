from django.db import models
from  django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel



'''
继承AbstractUser：用他的属性
继承BaseModel：共有的属性
'''
class User(AbstractUser,BaseModel):
    '''用户模型'''
    address= models.CharField(max_length=200,null=True)
    receiver= models.CharField(max_length=20,null=True)
    phone= models.CharField(max_length=20,null=True)
    postcode= models.CharField(max_length=10,null=True)
    # pwd= models.CharField(max_length=100,null=False)
    class Meta:
        db_table='df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name