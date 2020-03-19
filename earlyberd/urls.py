"""earlyberd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import path, re_path

from article import views as article_views
from home.views import (
    HomeView,
    LoginView,
    QuoteView,
    SignupView,
    EmailValidationView,
    logout_view,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('author/<pk>', article_views.AuthorView.as_view(), name='author'),
    path('articles', article_views.BrowseArticlesView.as_view()),
    path('article/<id>', article_views.ArticleView.as_view()),
    path('edit-article/<pk>', article_views.ArticleUpdateView.as_view()),
    path('delete-article/<pk>', article_views.ArticleDeleteView.as_view()),
    path('article', article_views.ArticleSubmissionView.as_view()),
    path('reading-list/<id>', article_views.ReadingListView.as_view()),
    path('my-articles/<id>', article_views.MyArticlesView.as_view()),
    path('signup', SignupView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', logout_view),
    path('quote', QuoteView.as_view()),
    path('verify-email', EmailValidationView.as_view(), name='verify-email'),
    path('', HomeView.as_view()),
]
