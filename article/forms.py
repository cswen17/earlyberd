from django import forms
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import UploadedFile

from .form_utils import (
    CoverImageField,
    CoverImageThumbnailField,
    UserField,
)
from .models import Article, Author, ReadingList


class ArticleForm(forms.ModelForm):

    """
    Form for converting Jodit form data to our backend model
    """

    title = forms.CharField(label='Title', max_length=2048)
    # todo: replace with django user
    reading_lists = forms.ModelMultipleChoiceField(ReadingList.objects.all(), label='Would you like your article to be part of any reading lists?')
    html = forms.CharField(label='Write Your Article Below:', widget=forms.Textarea)
    cover_image = CoverImageField(label='Select a Cover Image (1440x400)')
    cover_image_thumbnail = CoverImageThumbnailField(label='Design a Thumbnail (256x124)')

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('user', None)
        super(ArticleForm, self).__init__(*args, **kwargs)
        if request_user:
            self._user = request_user
            self.fields['author'] = forms.ModelChoiceField(
                queryset=Author.objects.filter(user__id=request_user.id), 
                limit_choices_to={'user__id': request_user.id},
                empty_label=None,
            )

    def clean_cover_image(self):
        cleaned_data = self.cleaned_data
        tmp_cover_image = cleaned_data['cover_image']
        if isinstance(tmp_cover_image, UploadedFile):
            print('$$$Got here')
            ret_val = ImageFile(tmp_cover_image)
            print('$$$')
            print(dir(ret_val))
            print('$$$')
            return ret_val
        image = getattr(tmp_cover_image, 'image', None)
        if not image:
            return tmp_cover_image
        height = image.height
        width = image.width
        """
        if height > 256:
            raise ValidationError(
                'Invalid height {}. Must be < 256'.format(height))
        if width > 256:
            raise ValidationError(
                'Invalid width {}. Must be < 256'.format(width))
        """
        return tmp_cover_image

    def clean_cover_image_thumbnail(self):
        thumbnail = self.cleaned_data['cover_image_thumbnail']
        if isinstance(thumbnail, UploadedFile):
            print('%%%Got here')
            return ImageFile(thumbnail)
        return thumbnail

    def save(self, commit=True):
        instance = super(ArticleForm, self).save(commit=commit)
        reading_lists = self.cleaned_data['reading_lists']
        covimg = self.cleaned_data['cover_image']
        print('########')
        print(covimg.read())
        print('########')
        for reading_list in reading_lists:
            reading_list.articles.add(instance)
            reading_list.save()
        return instance

    class Meta:
        model = Article
        fields = [
            'cover_image',
            'cover_image_thumbnail',
            'title',
            'author',
            'reading_lists',
            'html',
        ]


class ConfirmArticleDeleteForm(forms.Form):
    """
    A form that lists which reading lists the article will be
    removed from
    """
    reading_lists = forms.ModelMultipleChoiceField(
        ReadingList.objects.all(),
        label='Your article will be removed from these reading lists:',
        disabled=True,
    )


class AuthorForm(forms.ModelForm):
    """
    A form for user settings
    """

    picture = forms.ImageField(label='Profile Picture:')
    user = UserField(label='')

    def clean(self, **kwargs):
        """
        Uses lookups into cleaned_data to update certain user fields
        """
        user = self.instance.user
        cleaned_user = self.cleaned_data.get('user')
        first_name = cleaned_user.get('first_name', '')
        last_name = cleaned_user.get('last_name', '')
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        self.cleaned_data['user'] = user
        return self.cleaned_data

    class Meta:
        model = Author
        fields = ['picture', 'user']

