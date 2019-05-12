from django.db import models


class ConfigurableManager(models.Manager):
    """
    Manager for the Configurable object
    """

    def o(self):
        return self.get_queryset().first()


class QuoteManager(models.Manager):
    """
    Manager for the Quote object
    """

    def o(self):
        return self.get_queryset().last()
