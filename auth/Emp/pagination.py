from rest_framework import pagination
from rest_framework.response import Response
from rest_framework import status 


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param='records'
    max_page_size=5
    
    
    def get_paginated_response(self, data):
        page=self.page
        return Response({
            'total_pages': page.paginator.num_pages,
            'count': page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        }, status=status.HTTP_200_OK)
    
