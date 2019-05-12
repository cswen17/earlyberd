from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    FormView,
    UpdateView,
)
from django.views.generic.list import ListView

from .forms import ArticleForm, AuthorForm, ConfirmArticleDeleteForm
from .models import Article, Author, ReadingList


class ArticleSubmissionView(CreateView):

    """
    Creates an Article for the Article Submission Area
    """

    template_name = 'submit.html'
    form_class = ArticleForm
    success_url = '/article' # Todo

    def get(self, request, *args, **kwargs):
        """
        Added permission checking
        Protects the WRITE page from non-authors
        """
        user = request.user
        author_group = user.groups.filter(name='Authors')
        if not author_group:
            raise PermissionDenied('You must be an author to view this page')
        res = super(ArticleSubmissionView, self).get(request, *args, **kwargs)
        return res

    def get_form_kwargs(self):
        kwargs = super(ArticleSubmissionView, self).get_form_kwargs()
        user = self.request.user
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ArticleView(View, TemplateResponseMixin):

    """
    Reads an Article
    """

    template_name = 'article.html'

    def get(self, request, *args, **kwargs):
        """
        Fetches a single article

        GET /articles/<id>
        """
        article_uuid = kwargs.get('id')
        articles = Article.objects.filter(uuid=article_uuid)
        if articles is None:
            return HttpResponseNotFound('Could not find article')

        article = articles.first()
        # Put article.html in a template
        tokens = article.cover_image.name.split('article/static')
        return self.render_to_response({
            'article': article,
            'article_url': tokens[-1],
            'user': request.user,
        })


class BrowseArticlesView(ListView):

    """
    Lists all articles
    """

    model = Article
    template_name = 'list.html'

    def get_queryset(self, **kwargs):
        return self.model.objects.nonempty()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        remaining = len(self.object_list) % 6
        end = len(self.object_list) - remaining
        context_data['articles'] = self.object_list[:end]
        context_data['remaining'] = self.object_list[end:]
        context_data['remain_padding'] = [0]*(6 - remaining)
        if remaining == 0:
            context_data['remaining'] = Article.objects.none()

        # reading lists
        reading_lists = ReadingList.objects.for_article_list_page()
        context_data['reading_lists'] = reading_lists
        context_data['user'] = self.request.user
        return context_data


class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'article/article_update_form.html'
    success_url = '/'

    def update(self, request, *args, **kwargs):
        """
        Checks group before updating
        """
        user = getattr(request, 'user', None)
        if not user:
            message = (
                'I could not find the user associated with your'
                'request. This article will not be updated right'
                'now. Please make sure you are logged in, then'
                'try again.'
            )
            return HttpResponseForbidden(message)
        authors = user.groups.filter(name='Authors')
        if not authors:
            return HttpResponseForbidden(
                'Only authors can edit their articles')
        res = super(ArticleUpdateView, self).update(request, *args, **kwargs)
        return res

    def get_success_url(self):
        res = super(ArticleUpdateView, self).get_success_url()
        user = getattr(self.request, 'user', None)
        if user:
            return '/my-articles/{}'.format(user.id)
        return res


class ArticleDeleteView(DeleteView, FormView):
    model = Article
    form_class = ConfirmArticleDeleteForm
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        """
        Checks model permissions before deleting
        """
        user = getattr(request, 'user', None)
        if not user:
            message = (
                'There was no user found in your request. Try again.'
            )
            return HttpResponseForbidden(message)
        authors = user.groups.filter(name='Authors')
        if not authors:
            return HttpResponseForbidden(
                'Forbidden: You are not part of the authors group')
        res = super(ArticleDeleteView, self).delete(
            request, *args, **kwargs)
        return res

    def get_success_url(self):
        res = super(ArticleDeleteView, self).get_success_url()
        user = getattr(self.request, 'user', None)
        if user:
            return '/my-articles/{}'.format(user.id)
        return res


######################
# Reading List Views #
######################

class ReadingListView(View, TemplateResponseMixin):
    template_name = 'topic.html'

    def get(self, request, *args, **kwargs):
        """
        Reads a single reading list

        GET /reading-list/<id>
        """
        reading_list_id = kwargs.get('id')

        reading_lists = ReadingList.objects.filter(id=reading_list_id)
        if reading_lists is None:
            return HttpResponseNotFound('Could not find reading list')

        reading_list = reading_lists.first()
        return self.render_to_response({
            'reading_list': reading_list,
            'articles': reading_list.articles.all(),
            'user': request.user,
            'view': self,
        })


################
# Author Views #
################

class AuthorView(UpdateView):
    model = Author
    form_class = AuthorForm
    template_name_suffix = '_update_form'

    def get_initial(self):
        author = self.object
        if author is None:
            return super(AuthorView, self).get_initial()
        user = author.user
        kwargs = {}
        kwargs['user'] = ' '.join([user.first_name, user.last_name])
        return kwargs

    def get_form_kwargs(self):
        kwargs = super(AuthorView, self).get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super(AuthorView, self).get_context_data(**kwargs)
        context_data['user'] = self.request.user
        return context_data


class MyArticlesView(ListView):
    model = Article
    template = 'my_articles.html'

    def get_queryset(self):
        user_id = self.request.user.id

        authors = Author.objects.filter(user__id=user_id)
        if not authors:
            return Article.objects.none()
        author = authors.first()
        return author.article_set.nonempty()

