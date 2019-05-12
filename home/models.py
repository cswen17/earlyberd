from django.db import models

from .managers import ConfigurableManager, QuoteManager


class Configurable(models.Model):
    """
    Includes some configurable text from the home page
    """

    welcome_title = models.CharField(max_length=512)
    welcome_text = models.CharField(max_length=2048)
    welcome_image = models.ImageField(upload_to='home/static/media')

    single = ConfigurableManager()

    def welcome_image_url(self):
        tokens = self.welcome_image.url.split('home/static/')
        return tokens[-1]

    def __str__(self):
        return self.welcome_title


class Quote(models.Model):

    """
    Represents a quote or passage to share with everybody
    on a regular interval
    """

    comment = models.CharField(max_length=2048)
    quote = models.CharField(max_length=1024)
    quoter = models.CharField(max_length=256)
    image = models.ImageField(upload_to='home/static/media')
    interval = models.PositiveIntegerField()

    single = QuoteManager()

    def cover_image_url(self):
        tokens = self.image.url.split('home/static/')
        return tokens[-1]

    def __str__(self):
        return '[{}]- {}...'.format(self.comment, self.quote[:56])
