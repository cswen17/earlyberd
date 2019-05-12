from json.tool import json
import re
import os

from django import template
from django.conf import settings
from django.templatetags.static import static

from article.models import Author


register = template.Library()
DEFAULT_JSON_PATH = os.path.join(
    settings.BASE_DIR,
    'article',
    'templates',
    'sitemap.json'
)


@register.tag
def breadcrumb(parser, token):
    """
    Given a user, finds the corresponding author and renders
    their profile picture

    value must be the user object
    arg must be the user's ID
    """
    """
    user_id = int(arg)
    authors = Author.objects.filter(user__id=user_id)
    if authors is None:
        return static('avatar-stock.svg')

    author = authors.first()
    profile_picture_path = author.cover_image_url()
    return static(profile_picture_path)
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            '{} tag requires arguments'.format(token.contents.split()[0])
        )
    m = re.search(r'as (\w+) (silent)*( custom\[.*\])*', arg)
    if not m:
        raise template.TemplateSyntaxError(
            "{} tag had invalid arguments".format(tag_name)
        )
    var_name, is_silent, custom = m.groups()
    if custom:
        parse_custom = re.search(r'custom\[(.+)\]', custom)
        custom = parse_custom.groups()[0]
    return BreadcrumbNode(var_name, is_silent, custom)


class BreadcrumbNode(template.Node):
    def __init__(self, var_name, is_silent, custom):
        self.is_silent = is_silent == 'silent'
        self.var_name = var_name
        self.lookup_tree = LookupTreeSet()
        self.lookup_tree.from_json()
        self.custom = custom

    def render(self, context):
        if self.custom:
            result, context = self.custom_render(context)
            return result
        view = context.get('view', None)
        if not view:
            return ''
        view_request = getattr(view, 'request', None)
        if not view_request:
            return ''
        path = getattr(view_request, 'path', None)
        if not path:
            return ''
        lookup_list = self.lookup_tree.lookup(
            path,
            eq_func=self._url_contained,
        )
        context[self.var_name] = lookup_list
        if self.is_silent:
            return ''
        return lookup_list

    def custom_render(self, context):
        """
        Looks up everything up to the parent, lets the view
        write the breadcrumb for the child
        """
        lookup_list = self.lookup_tree.lookup(
            self.custom,
            eq_func=self._url_equals
        )
        lookup_list = lookup_list[:-1]
        context[self.var_name] = lookup_list
        if self.is_silent:
            return '', context
        return lookup_list, context

    def _url_equals(self, curr, target):
        return curr['url'] == target

    def _url_contained(self, curr, target):
        return curr['url'] in target and curr['url'] != '/'


class LookupTreeSet(object):
    def __init__(self, *args, **kwargs):
        self.root = None
        self.num_nodes = 0

    def add(self, parent_node, data):
        curr_node = None
        if isinstance(parent_node, LookupTreeNode):
            curr_node = LookupTreeNode(data, parent=parent_node)
            parent_node.children.append(curr_node)
            self.num_nodes += 1
            return curr_node
        elif parent_node is None and self.num_nodes == 0:
            self.root = LookupTreeNode(data, parent=None)
            self.num_nodes += 1
            return self.root
        else:
            parent = self._bfs(parent_node)
            curr_node = LookupTreeNode(data, parent=parent)
            parent.children.append(curr_node)
            self.num_nodes += 1
            return curr_node

    def from_json(self, js_str='', file_path=DEFAULT_JSON_PATH):
        node_dict = {}
        if js_str:
            node_dict = json.loads(js_str)
        elif file_path:
            sitemap = open(file_path, 'r')
            site_js_str = sitemap.read()
            node_dict = json.loads(site_js_str)
        else:
            return self

        self._parse_sitemap_json(node_dict)
        return self

    def lookup(self, target, eq_func=None):
        node = self._bfs(target, eq_func)
        path = []
        while node is not None:
            path.insert(0, node.data)
            node = node.parent
        return path

    def _parse_sitemap_json(self, node_dict):
        site = node_dict.get('site', []) 
        parent = self.root
        for node in site:
            self._parse_children(node, self.root)

    def _parse_children(self, node, parent):
        leaf = self.add(parent, dict(name=node['name'], url=node['url']))
        children = node['children']
        for child in children:
            self._parse_children(child, leaf)

    def _bfs(self, data, eq_func=None):
        curr_node = None
        visited_nodes = set()
        nodes = [self.root]
        # bfs for parent_node's data
        while len(visited_nodes) < self.num_nodes:
            curr_node = nodes.pop()
            if curr_node in visited_nodes:
                continue
            for child in curr_node.children:
                nodes.insert(0, child)
            visited_nodes.add(curr_node)
            if eq_func:
                if eq_func(curr_node.data, data):
                    return curr_node
            elif curr_node.data == data:
                return curr_node
        return None

    def __str__(self):
        if self.root is None and self.num_nodes == 0:
            return '[Empty]'
        curr_node = None
        nodes = [(self.root, 0)]
        result = ''
        while nodes:
            curr_node, lvl = nodes.pop()
            for child in curr_node.children:
                nodes.insert(0, (child, lvl+1))
            result += '\t'*lvl
            result += '[{} -> {}]\n'.format(
                getattr(curr_node.parent, 'data', ''),
                curr_node.data
            )
        return result


class LookupTreeNode(object):
    def __init__(self, data, *args, **kwargs):
        self.data = data
        self.children = kwargs.get('children', [])
        self.parent = kwargs.get('parent', None)

    def set_parent_node(self, parent_node):
        self.parent = parent_node

    def __str__(self):
        return '({})'.format(self.data)
