from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=150, unique=True)
    linked_articles = models.ManyToManyField("Article")