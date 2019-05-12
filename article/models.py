import os
import socket
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files.images import ImageFile
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from .managers import ArticleManager, ReadingListManager


STOCK_IMAGE_PATH = os.path.join(settings.BASE_DIR, 'article', 'static', 'blank-square.png')


def default_image():
    stock_image = open(STOCK_IMAGE_PATH, 'r+b')
    return ImageFile(stock_image)


def default_author():
    return Author.objects.filter(user__email='skip@heitzig.com').first()


class Author(models.Model):

    """
    The Author of a Christian Article
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    is_email_validated = models.BooleanField(default=False)
    email_validation_token = models.UUIDField(default=uuid.uuid4)
    picture = models.ImageField(
        upload_to='article/static/media',
        default=default_image,
        height_field='picture_height',
        width_field='picture_width',
    )
    picture_height = models.IntegerField()
    picture_width = models.IntegerField()

    def get_absolute_url(self):
        return reverse('author', kwargs={'pk': self.pk})

    def default_image():
        profile_pic_path = os.path.join(
            settings.BASE_DIR,
            'home',
            'static',
            'avatar-stock.svg',
        )
        stock_image = open(profile_pic_path, 'r+b')
        return ImageFile(stock_image)

    def cover_image_url(self):
        tokens = self.picture.url.split('article/static/')
        return tokens[-1]

    def full_name(self):
        first_name = self.user.first_name
        last_name = self.user.last_name
        return '{} {}'.format(first_name, last_name)

    def email_validated(self):
        return self.user.is_active and self.is_email_validated

    def generate_email_validation_link(self):
        token = self.email_validation_token
        url = reverse('verify-email')
        host = Site.objects.get_current().domain
        protocol = 'https://'
        port = ''
        if settings.DEBUG:
            port = ':8000'
            protocol = 'http://'
        return '{}{}{}{}?token={}'.format(protocol, host, port, url, token)

    def __str__(self):
        first_name = getattr(self.user, 'first_name', '')
        last_name = getattr(self.user, 'last_name', '')
        return ' '.join([first_name, last_name])


class Article(models.Model):

    """
    A Christian Article written in HTML
    """

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(max_length=2048)
    html = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    cover_image = models.ImageField(
        upload_to='article/static/media/',)
    cover_image_thumbnail = models.ImageField(
        upload_to='article/static/media/',)
    created_at = models.DateTimeField(auto_now_add=True)
    reading_lists = models.ManyToManyField('ReadingList', blank=True)

    objects = ArticleManager()

    def __str__(self):
        return '{} {}'.format(self.title, self.author)

    def cover_image_url(self):
        tokens = self.cover_image.url.split('article/static/')
        return tokens[-1]

    def short_title(self):
        if len(self.title) > 14:
            return '{}...'.format(self.title[:14])
        return self.title

    def empty(empty_title='~EMPTY0'):
        empty = Article.objects.filter(title=empty_title).first()
        if not empty:
            stock_image = default_image()
            stock_author = default_author()
            empty = Article.objects.create(
                author=stock_author,
                title=empty_title,
                cover_image=stock_image,
            )
        return empty

    def is_empty(self):
        return 'EMPTY' in self.title


class ReadingList(models.Model):

    """
    A List of Articles recommended for reading to the user
    """

    name = models.CharField(max_length=256)
    description = models.CharField(max_length=2048)
    articles = models.ManyToManyField('Article', blank=True)

    objects = ReadingListManager()

    def __str__(self):
        return '{}: {} ({} articles)'.format(self.name, self.description, self.articles.count())
