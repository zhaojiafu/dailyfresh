from django.db import models
from db.base_model import BaseModel
from tinymce


class GoodsType(BaseModel):
    '''商品类型模型类'''
    name = models.CharField(max_length=20, verbose_name="种类名称")
    logo = models.CharField(max_length=20, verbose_name="标识")
    image = models.ImageField(upload_to='type', verbose_name="商品类型照片")

    class Meta:
        db_table = 'df_goods_type'
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name



class GoodsSKU(BaseModel):
    '''商品SKU模型类'''
    status_choice = (
        (0,'下线'),
        (1,'上线'),
    )
    type = models.ForeignKey('GoodsType',verbose_name='商品种类')
    goods = models.ForeignKey('Goods',verbose_name='商品SPU')
    name = models.CharField(max_length=20,verbose_name='商品名称')
    desc = models.CharField(max_length=256,verbose_name='商品简介')
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品价格')
    unite = models.CharField(max_length=20,verbose_name='商品单位')
    image = models.ImageField(upload_to='goods',verbose_name='商品图片')
    stock = models.IntegerField(default=1,verbose_name='商品库存')
    sales = models.IntegerField(default=0,verbose_name='商品销量')
    status = models.SmallIntegerField(default=1,choices=status_choice,verbose_name='商品状态')

    class Meta:
        db_table = 'df_goods_sku'
        verbose_name = '商品'
        verbose_name_plural = verbose_name


class Goods(BaseModel):
    '''商品SPU模型类'''
    name = models.CharField(max_length=20,verbose_name='商品SPU名称')
    # 富文本类型:带有格式的文本
    detail = HTMLF
