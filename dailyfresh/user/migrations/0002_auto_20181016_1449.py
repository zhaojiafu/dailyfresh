# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('updete_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('address', models.CharField(verbose_name='收货地址', max_length=200)),
                ('receiver', models.CharField(verbose_name='收件人', max_length=20)),
                ('phone', models.CharField(verbose_name='收件人电话', max_length=20)),
                ('postcode', models.CharField(verbose_name='收件人邮编', null=True, max_length=10)),
            ],
            options={
                'verbose_name': '地址',
                'verbose_name_plural': '地址',
                'db_table': 'df_address',
            },
        ),
        migrations.RemoveField(
            model_name='user',
            name='address',
        ),
        migrations.RemoveField(
            model_name='user',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='user',
            name='postcode',
        ),
        migrations.RemoveField(
            model_name='user',
            name='receiver',
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(verbose_name='所属账户', to=settings.AUTH_USER_MODEL),
        ),
    ]
