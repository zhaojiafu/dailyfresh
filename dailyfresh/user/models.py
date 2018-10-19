from django.db import models
from  django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel



'''
继承AbstractUser：用他的属性
继承BaseModel：共有的属性
'''
class User(AbstractUser,BaseModel):
    '''用户模型'''

    # pwd= models.CharField(max_length=100,null=False)
    class Meta:
        db_table='df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Address(BaseModel):
    user = models.ForeignKey("User",verbose_name="所属账户")
    addr = models.CharField(max_length=200,verbose_name="收货地址")
    receiver = models.CharField(max_length=20, verbose_name="收件人")
    phone = models.CharField(max_length=20, verbose_name="收件人电话")
    postcode = models.CharField(max_length=10, null=True, verbose_name="收件人邮编")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")

    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name


