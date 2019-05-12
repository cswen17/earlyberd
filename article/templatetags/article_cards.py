from json.tool import json
import re
import os

from django import template
from django.contrib.auth.models import User

from article.models import Article, Author


register = template.Library()


@register.tag
def article_card(parser, token):
    """
    Given an article object, renders the card for the object
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            '{} tag requires arguments'.format(token.contents.split()[0])
        )
    syntax = (
        '(\w+) as (\w+) (silent)*( per_row\[\d+\])*'
        '( include_edit_button)*( include_delete_button)*'
        '( include_author_name)*( deck)*( group)*'
    )
    regex_syntax = r'{}'.format(syntax)
    m = re.search(regex_syntax, arg)
    if not m:
        raise template.TemplateSyntaxError(
            "{} tag had invalid arguments".format(tag_name)
        )
    context_var_name, var_name, is_silent, per_row, edit, delete, credit, deck, group = m.groups()
    if per_row:
        parse_per_row = re.search(r'per_row\[(\d+)\]', per_row)
        per_row = parse_per_row.groups()[0]
    return ArticleCardgroupNode(
        context_var_name,
        var_name=var_name,
        is_silent=is_silent,
        per_row=per_row,
        edit=edit,
        delete=delete,
        credit=credit,
        deck=deck,
        group=group,
    )


class ArticleCardgroupNode(template.Node):

    container_template = 'article-card-container.html'
    row_template = 'article-card-row.html'

    def __init__(self, context_var_name, *args, **kwargs):
        self.context_var_name = context_var_name
        self.var_name = kwargs.get('var_name', '')
        self.is_silent = kwargs.get('is_silent', False)
        self.per_row = kwargs.get('per_row', 6)
        self.include_edit_button = kwargs.get('edit', '')
        self.include_delete_button = kwargs.get('delete', '')
        self.include_author_name = kwargs.get('credit', '')
        self.is_deck = kwargs.get('deck', '')
        self.is_group = kwargs.get('group', '')

    def render(self, context):
        """
        Extracts the Article queryset, loops through in increments
        of <per_row>, and renders each article from the queryset

        Usage:
            All items in square brackets [] are optional.

            card_group <queryset> as <variable name> [is_silent]
            [per_row[4|6]] [include_edit_button]
            [include_delete_button] [include_author_name] group|deck

            where <queryset> is the name of the context variable
            containing the Article objects (required)

            where variable_name is the name of the template variable
            the result will be stored in (required)

        Examples:

        {% card_group objects as article_cards silent per_row[6] include_edit_button include_delete_button include_author_name deck %}
            Outputs articles as cards in rows of 6, using the bootstrap
            card-deck container class, includes edit buttons, delete
            buttons, and author name
        """
        queryset = context.get(self.context_var_name, Article.objects.none())
        objects, tail = (queryset, [])
        remainder = len(queryset) % int(self.per_row)
        if remainder != 0:
            whole = int(len(queryset) / int(self.per_row))
            pivot = whole * int(self.per_row)
            objects, tail = (objects[:pivot], objects[pivot:])
        divided_objects = []
        for i in range(0, len(objects), int(self.per_row)):
            divided_objects.append((objects[i:i+int(self.per_row)], []))
        if tail:
            remain = int(self.per_row) - remainder
            padding = ['EMPTY'] * remain
            divided_objects.append((tail, padding))
        # for tail, convert tail into tail and padding
        card_rows = []
        for (row, padding) in divided_objects:
            subcontext = context.new({
                'row': row,
                'padding': padding,
                'edit': self.include_edit_button == 'include_edit_button',
                'delete': self.include_delete_button == 'include_delete_button',
                'container_type': self._container_type(),
                'include_author_name': self.include_author_name,
                'include_edit_button': self.include_edit_button,
                'include_delete_button': self.include_delete_button,
            })
            row_template = context.template.engine.get_template(
                self.row_template,
            )
            card_row = row_template.render(subcontext)
            card_rows.append(card_row)
        container_context = context.new({
            'card_rows': card_rows,
        })
        container_template = context.template.engine.get_template(
            self.container_template,
        )
        container = container_template.render(container_context)
        context[self.var_name] = container
        if self.is_silent:
            return ''
        else:
            return container

    def _empty_in_memory(self):
        user = User.objects.first()
        author = Author(user=user)
        article = Article(author=author, title='EMPTY')
        return article

    def _container_type(self):
        if self.is_deck == ' deck':
            return 'card-deck'
        elif self.is_group == ' group':
            return 'card-group'
        else:
            return ''

    def _render_card_row(self, subcontext):
        """
        only render a card-group row
        cache the template object in render_context to avoid
        reparsing and loading when used in a for loop

        row
        container_type
        """
        pass
