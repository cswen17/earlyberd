import random

from django.db import models


class ReadingListManager(models.Manager):

    """
    A custom manager that limits the number of items returned
    """

    def for_home_page(self):
        """
        A helper function that selects a randomized ordering of
        articles to display on the home page.

        3 cases:
          1. < 6 articles in reading list:
            Returns all articles, then pads the remaining slots
            with empty articles.
          2. >= 6 articles in reading list, but empty articles remain:
            Returns a random ordering of the nonempty articles
          3. >= 6 articles in reading list, no empty articles:
            Returns a random ordering of articles
        """
        all_reading_lists = super().get_queryset()
        reading_lists = self.random_sample(all_reading_lists, 'name', 6)
        return self._limit_to_six_articles(reading_lists)

    def _limit_to_six_articles(self, reading_lists):
        reading_list_values = reading_lists.values()
        for reading_list_value in reading_list_values:
            reading_list = reading_lists.get(name=reading_list_value['name'])
            all_articles = reading_list.articles
            if all_articles.nonempty_count() >= 6:
                all_articles = all_articles.nonempty()
                articles = self.random_sample(all_articles, 'title', 6)
                reading_list_value['articles'] = articles.order_by('title')
            elif all_articles.nonempty_count() < 6:
                pad_set = all_articles.exclude(title__contains='EMPTY')
                articles = all_articles.pad_with_empty(pad_set, 6)
                reading_list_value['articles'] = articles.order_by('title')
        return reading_list_values

    def for_article_list_page(self):
        """
        A helper function that selects a randomized ordering of
        articles to display on the browse page.

        The articles are limited to 6 per Reading List
        There is no limit to the fetched Reading Lists
        """
        reading_lists = super().get_queryset()
        return self._limit_to_six_articles(reading_lists) 


    def random_sample(self, queryset, lookup_field, population):
        """
        """
        if not queryset or queryset.count() < population:
            return queryset
        names = queryset.values_list(lookup_field)
        names = [tpl[0] for tpl in names]
        if not names:
            return queryset
        random_sample = random.sample(names, population)
        query_filter_key = '{}__in'.format(lookup_field)
        query_filters = {
            query_filter_key: random_sample, 
        }
        return queryset.filter(**query_filters)


class ArticleManager(models.Manager):

    """
    Manager with helper functions for creating shell articles
    """

    def pad_with_empty(self, queryset, modulus):
        if queryset.count() % modulus != 0 or queryset.count() == 0:
            need = modulus - (queryset.count() % modulus)
            titles_to_search = [i for i in range(need)]
            titles_to_search = [
                "~EMPTY{}".format(i) for i in titles_to_search]
            for title in titles_to_search:
               self.model.empty(empty_title=title)
            empty_articles = super().get_queryset().filter(
                    title__in=titles_to_search)
            queryset = queryset.union(empty_articles)
            print(queryset)
        return queryset

    def order_by_title(self):
        return self.get_queryset().order_by('title')

    def nonempty_count(self):
        queryset = self.get_queryset().exclude(title__contains='EMPTY')
        return queryset.count()

    def nonempty(self):
        return self.get_queryset().exclude(title__contains='EMPTY')
