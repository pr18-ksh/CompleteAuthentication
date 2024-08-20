from rest_framework.generics import ListAPIView
from .serializers import EmpSerializer
from .models import EmployeeData
from .pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

class EmpListView(ListAPIView): 
   authentication_classes = [TokenAuthentication]  
   permission_classes = [IsAuthenticated]
   pagination_class = CustomPagination
   
   def get(self, request):
        # Get all employee data
        employees = EmployeeData.objects.all().order_by('emp_id')
        
        page = self.paginate_queryset(employees)
        
        if page is not None:
            serializer = EmpSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
         
        serializer = EmpSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

   def post(self, request):
        # Create new employee data
        serializer = EmpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
    
       