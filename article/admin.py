from django.contrib import admin
from .models import Article, Author, ReadingList


# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    """
    Default Model Admin Page for Articles
    """
    pass


class ReadingListAdmin(admin.ModelAdmin):
    """
    Default Model Admin Page for Reading Lists
    """
    pass


class AuthorAdmin(admin.ModelAdmin):
    """
    Default Model Admin Page for Authors
    """
    pass


admin.site.register(Article, ArticleAdmin)
admin.site.register(ReadingList, ReadingListAdmin)
admin.site.register(Author, AuthorAdmin)
