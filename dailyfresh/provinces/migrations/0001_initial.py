# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Areas',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('aname', models.CharField(unique=True, null=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Citys',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('cname', models.CharField(unique=True, null=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Provinces',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('pname', models.CharField(unique=True, null=True, max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='citys',
            name='cprovince',
            field=models.ForeignKey(to='provinces.Provinces'),
        ),
        migrations.AddField(
            model_name='areas',
            name='acity',
            field=models.ForeignKey(to='provinces.Citys'),
        ),
    ]
