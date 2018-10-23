# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('provinces', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testappf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('add', models.CharField(max_length=20, blank=True, null=True)),
            ],
            options={
                'db_table': 'testappf',
                'managed': False,
            },
        ),
        migrations.RemoveField(
            model_name='areas',
            name='acity',
        ),
        migrations.RemoveField(
            model_name='citys',
            name='cprovince',
        ),
        migrations.DeleteModel(
            name='Areas',
        ),
        migrations.DeleteModel(
            name='Citys',
        ),
        migrations.DeleteModel(
            name='Provinces',
        ),
    ]
