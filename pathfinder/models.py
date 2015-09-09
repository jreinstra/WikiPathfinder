from django.db import models

# Create your models here.
class Article(models.Model):
    """Stores information about downloaded articles."""
    
    title = models.CharField(max_length=150, unique=True)
    # JSON list of article titles
    linked_articles = models.TextField(blank=True)
    
    # Info about state of article
    downloaded = models.BooleanField(default=False)
    filled = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title