# Generated by Django 2.1.7 on 2019-04-02 14:10
import os

from django.conf import settings
from django.core.files.images import ImageFile
from django.db import migrations


def seed_data(apps, schema_editor):
    ###############
    # Seed Groups #
    ###############
    Permission = apps.get_model('auth', 'Permission')
    article_permissions = Permission.objects.filter(
        codename__contains='article')

    Group = apps.get_model('auth', 'Group')
    authors_group = Group.objects.create(name='Authors')
    authors_group.permissions.set(article_permissions)
    authors_group.save()

    ###############
    # Seed Author #
    ###############
    User = apps.get_model('auth', 'User')
    user = User.objects.create(
        username='skip@heitzig.com',
        email='skip@heitzig.com',
        first_name='Skip',
        last_name='Heitzig',
    )
    #user.set_password('scarletcordconnectsbible')
    #user.groups.set([authors_group])
    user.save()

    Author = apps.get_model('article', 'Author')
    author = Author.objects.create(user=user)

    ################
    # Seed Article #
    ################
    Article = apps.get_model('article', 'Article')

    article_path = os.path.join(
        settings.BASE_DIR,
        'home',
        'static',
        'scarlet-cord-connects-bible.html')
    scarlet_cord = open(article_path, 'r+').readlines()
    scarlet_cord_html = ''.join(scarlet_cord).replace('\n', '<br>')

    top_50_path = os.path.join(
        settings.BASE_DIR,
        'home',
        'static',
        'top-50.html',
    )
    top_50 = open(top_50_path, 'r+').readlines()
    top_50_html = ''.join(top_50).replace('\n', '<br>')

    # note: come up with different cover images
    cover_image_path = os.path.join(
        settings.BASE_DIR,
        'article',
        'static',
        'media',
        'scarlet-bible.jpg'
    )
    cover_image_file = open(cover_image_path, 'r+b')
    cover_image = ImageFile(cover_image_file)

    stock_article = Article.objects.create(
        title='How a Scarlet Cord Connects the Bible',
        html=scarlet_cord_html,
        author=author,
        cover_image=cover_image,
        cover_image_height=cover_image.height,
        cover_image_width=cover_image.width,
    )

    ####################
    # Seed ReadingList #
    ####################
    ReadingList = apps.get_model('article', 'ReadingList')

    names_and_descriptions = {
        'Inspiration': 'Renew your faith with these inspirational thoughts',
        "Pastor's Pick": 'A selection of curated articles picked by pastors',
        'Family': 'How to live a Christian life with your family',
        'Diligence': "Small acts you can do every day in Christ's name",
        'Holidays': 'Pause for reflection around the holidays',
    }
    article_queryset = Article.objects.filter(uuid=stock_article.uuid)

    for name, description in names_and_descriptions.items():
        reading_list = ReadingList.objects.create(
            name=name,
            description=description,
        )
        reading_list.articles.set(article_queryset)
        stock_article.reading_lists.add(reading_list)
        stock_article.save()


def delete_data(apps, schema_editor):
    Article = apps.get_model('article', 'Article')
    ReadingList = apps.get_model('article', 'ReadingList')

    Article.objects.all().delete()
    ReadingList.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=delete_data),
    ]
