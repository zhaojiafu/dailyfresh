# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_address_is_default'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='address',
            new_name='addr',
        ),
    ]
