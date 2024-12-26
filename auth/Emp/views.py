from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import EmployeeData
from .serializers import EmpSerializer


class EmployeeAPI(APIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        # Allow unauthenticated access for GET requests
        if self.request.method == 'GET':
            return [AllowAny()]
        # Require authentication for other requests
        return [IsAuthenticated()]

    @swagger_auto_schema(
        responses={200: EmpSerializer(many=True)},
        operation_description="Retrieve list of employees",
        # security=[]
    )
    def get(self, request, pk=None):
        if pk:
            # Retrieve a single employee
            try:
                employee = EmployeeData.objects.get(pk=pk)
            except EmployeeData.DoesNotExist:
                return Response({"status": 404, "message": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = EmpSerializer(employee)
            return Response({"status": 200, "payload": serializer.data})

        # Pagination parameters
        page_size = int(request.query_params.get('page_size', 50))
        page = int(request.query_params.get('page', 1))

        # Calculate start and end indexes
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        # Get all employees and count total entries
        employees = EmployeeData.objects.all().order_by('emp_id')
        total_employees = employees.count()

        # Retrieve employees for the current page
        paginated_employees = employees[start_index:end_index]
        serializer = EmpSerializer(paginated_employees, many=True)

        # Determine if there are next or previous pages
        has_next = end_index < total_employees
        has_previous = start_index > 0
        next_page = page + 1 if has_next else None
        previous_page = page - 1 if has_previous else None

        # Build response data with employee data and pagination metadata
        response_data = {
            "status": 200,
            "data": serializer.data,
            "pagination": {
                "total_count": total_employees,
                "page_size": page_size,
                "current_page": page,
                "has_next": has_next,
                "has_previous": has_previous,
                "next_page": next_page,
                "previous_page": previous_page,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=EmpSerializer,
        responses={201: EmpSerializer()},
        operation_description="Create a new employee",
        security=[{"Authorization": []}]
    )
    def post(self, request):
        # Authentication required for POST
        serializer = EmpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": 201, "payload": serializer.data, "message": "Employee created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response({"status": 400, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=EmpSerializer, 
        responses={200: EmpSerializer()}, 
        operation_description="Update an employee", 
        security=[{"Authorization": []}],  
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="Employee ID", type=openapi.TYPE_INTEGER)
        ],  
    )
    
    def put(self, request, pk):
        # Authentication required for PUT
        try:
            employee = EmployeeData.objects.get(pk=pk)
        except EmployeeData.DoesNotExist:
            return Response({"status": 404, "message": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmpSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": 200, "payload": serializer.data, "message": "Employee updated successfully"}
            )
        return Response({"status": 400, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={200: "Employee deleted successfully"},
        operation_description="Delete an employee",
        security=[{"Authorization": []}],
        operation_id="delete_employee",
    )
    def delete(self, request, pk):
        # Authentication required for DELETE
        try:
            employee = EmployeeData.objects.get(pk=pk)
        except EmployeeData.DoesNotExist:
            return Response({"status": 404, "message": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        employee.delete()
        return Response({"status": 200, "message": "Employee deleted successfully"})
