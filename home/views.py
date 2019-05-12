from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import SimpleTemplateResponse
from django.views import View
from django.views.generic.edit import CreateView, FormView

from .forms import AuthorLoginForm, AuthorSignupForm
from .models import Configurable, Quote
from article.models import Article, Author, ReadingList


# Create your views here.
class HomeView(View):

    """
    A Container for articles, quotes, and miscellaneous model display
    """

    def get(self, request, *args, **kwargs):
        return SimpleTemplateResponse(
            'home.html',
            context={
                'articles': Article.objects.order_by_title()[:6],
                'configurable': Configurable.single.o,
                'quote': Quote.single.o,
                'reading_lists': ReadingList.objects.for_home_page(),
                'user': request.user,
            }
        )


class LoginView(FormView):
    template_name = 'login.html'
    form_class = AuthorLoginForm
    success_url = '/'
    error_url = '/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        """
        Authenticates the user using django's authentication backend
        """
        username = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.author.email_validated():
            login(request, user)
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponseRedirect(self.error_url)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class SignupView(CreateView):
    template_name = 'signup.html'
    form_class =  AuthorSignupForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class EmailValidationView(View):
    """
    Given a valid email validation token, this view sets a user's
    email validated and is active status to True
    """

    def get(self, request, *args, **kwargs):
        """
        """
        post_data = getattr(request, 'GET', {})
        token = post_data.get('token', '')
        authors = Author.objects.filter(email_validation_token=token)
        if not authors:
            return HttpResponseNotFound(
                'Could not find user associated with token')
        author = authors.first()
        author.is_email_validated = True
        author.token = ''
        author.save()

        author.user.is_active = True
        author.user.save()
        return SimpleTemplateResponse('verify-email.html')
