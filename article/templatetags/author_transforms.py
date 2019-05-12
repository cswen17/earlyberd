from django import template
from django.templatetags.static import static

from article.models import Author


register = template.Library()


def avatar(value, arg):
    """
    Given a user, finds the corresponding author and renders
    their profile picture

    value must be the user object
    arg must be the user's ID
    """
    user_id = int(arg)
    authors = Author.objects.filter(user__id=user_id)
    if authors is None:
        return static('avatar-stock.svg')

    author = authors.first()
    profile_picture_path = author.cover_image_url()
    return static(profile_picture_path)


register.filter('avatar', avatar, is_safe=True)
register.tag('avatar', avatar)
