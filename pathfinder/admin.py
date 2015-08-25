from django.contrib import admin

from models import Article

# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    #filter_horizontal = ("linked_articles",)
    raw_id_fields = ("linked_articles",)
    search_fields = ("title",)
    
admin.site.register(Article, ArticleAdmin)