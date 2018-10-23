# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndexGoodBanner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('updete_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('image', models.ImageField(verbose_name='图片', upload_to='banner')),
                ('index', models.SmallIntegerField(verbose_name='展示顺序', default=0)),
                ('sku', models.ForeignKey(verbose_name='商品', to='goods.GoodsSKU')),
            ],
            options={
                'verbose_name_plural': '首页商品轮播商品',
                'db_table': 'df_index_banner',
                'verbose_name': '首页商品轮播商品',
            },
        ),
        migrations.CreateModel(
            name='IndexPromotionBanner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('updete_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('name', models.CharField(max_length=20, verbose_name='活动名称')),
                ('url', models.CharField(max_length=256, verbose_name='活动链接')),
                ('image', models.ImageField(verbose_name='活动照片', upload_to='banner')),
                ('index', models.SmallIntegerField(verbose_name='展示顺序', default=0)),
            ],
            options={
                'verbose_name_plural': '主页促销活动',
                'db_table': 'df_index_promotion',
                'verbose_name': '主页促销活动',
            },
        ),
        migrations.CreateModel(
            name='IndexTypeGoodsBanner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('updete_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('display_type', models.SmallIntegerField(choices=[(0, '标题'), (1, '图片')], verbose_name='展示类型', default=1)),
                ('index', models.SmallIntegerField(verbose_name='展示顺序', default=0)),
                ('sku', models.ForeignKey(verbose_name='商品SKU', to='goods.GoodsSKU')),
                ('type', models.ForeignKey(verbose_name='商品类型', to='goods.GoodsType')),
            ],
            options={
                'verbose_name_plural': '主页分类展示商品',
                'db_table': 'df_index_type_goods',
                'verbose_name': '主页分类展示商品',
            },
        ),
    ]
