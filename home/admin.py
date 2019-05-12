from django.contrib import admin
from .models import Configurable, Quote


class ConfigurableAdmin(admin.ModelAdmin):
    """
    Default Admin site form for Configurable Text
    """
    pass


class QuoteAdmin(admin.ModelAdmin):
    """
    Default Admin site form for Inspirational Quotes
    """
    pass


admin.site.register(Configurable, ConfigurableAdmin)
admin.site.register(Quote, QuoteAdmin)
