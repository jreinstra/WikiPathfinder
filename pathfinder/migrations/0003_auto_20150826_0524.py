# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pathfinder', '0002_article_downloaded'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='linked_articles',
        ),
        migrations.AddField(
            model_name='article',
            name='linked_articles',
            field=models.TextField(blank=True),
        ),
    ]
