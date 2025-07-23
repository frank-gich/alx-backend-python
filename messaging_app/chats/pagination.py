from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict


class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    Fetches 20 messages per page with custom response format.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Return a paginated style Response object with additional metadata.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
    
    def get_page_size(self, request):
        """
        Return the page size for this request.
        """
        if self.page_size_query_param:
            try:
                return int(request.query_params[self.page_size_query_param])
            except (KeyError, ValueError):
                pass
        return self.page_size


class ConversationPagination(PageNumberPagination):
    """
    Custom pagination class for conversations.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Return a paginated style Response object for conversations.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('conversations', data)
        ]))
    
    def get_page_size(self, request):
        """
        Return the page size for this request.
        """
        if self.page_size_query_param:
            try:
                return int(request.query_params[self.page_size_query_param])
            except (KeyError, ValueError):
                pass
        return self.page_size


class LimitOffsetMessagePagination(LimitOffsetPagination):
    """
    Alternative pagination using limit/offset for messages.
    Useful for infinite scrolling implementations.
    """
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100
    
    def get_paginated_response(self, data):
        """
        Return a paginated style Response object using limit/offset.
        """
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('limit', self.limit),
            ('offset', self.offset),
            ('results', data)
        ]))


class CustomCursorPagination(PageNumberPagination):
    """
    Custom cursor pagination for real-time message updates.
    Useful for chat applications where messages are frequently added.
    """
    page_size = 20
    ordering = '-timestamp'  # Most recent messages first
    cursor_query_param = 'cursor'
    page_size_query_param = 'page_size'
    
    def get_paginated_response(self, data):
        """
        Return a paginated response with cursor information.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count if hasattr(self, 'page') else len(data)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('messages', data)
        ]))
