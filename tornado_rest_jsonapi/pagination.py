# -*- coding: utf-8 -*-
# Imported from flask-rest-jsonapi
# https://github.com/miLibris/flask-rest-jsonapi

from urllib.parse import urlencode
from copy import deepcopy

DEFAULT_PAGE_SIZE = 20


def pagination_links(object_count, query, base_url):
    """Add pagination links to result

    Parameters
    ----------
    object_count: int
        number of objects in result
    query: QueryStringManager
        the managed querystring fields and values
    base_url: str
        the base url for pagination
    """
    links = {}
    new_query = deepcopy(query)
    links['self'] = base_url

    # compute self link
    if len(query):
        links['self'] += '?' + urlencode(query.queryitems)

    if query.pagination.get('size',
                            DEFAULT_PAGE_SIZE) != 0 and object_count > 1:
        # compute last link
        page_size = query.pagination.get('size', DEFAULT_PAGE_SIZE)
        last_page = int((object_count - 1) / page_size)

        if last_page > 0:
            links['first'] = links['last'] = base_url

            try:
                del new_query['page[number]']
            except KeyError:
                pass

            # compute first link
            if len(new_query):
                links['first'] += '?' + urlencode(new_query.queryitems)

            new_query['page[number]'] = last_page
            links['last'] += '?' + urlencode(new_query.queryitems)

            # compute previous and next link
            current_page = query.pagination.get('number', 0)
            if current_page > 0:
                new_query['page[number]'] = current_page - 1
                links['prev'] = '?'.join((base_url,
                                          urlencode(new_query.queryitems)))
            if current_page < last_page:
                new_query['page[number]'] = current_page + 1
                links['next'] = '?'.join((base_url,
                                          urlencode(new_query.queryitems)))

    return links
