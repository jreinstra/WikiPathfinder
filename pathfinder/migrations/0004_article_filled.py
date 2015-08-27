# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pathfinder', '0003_auto_20150826_0524'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='filled',
            field=models.BooleanField(default=False),
        ),
    ]
