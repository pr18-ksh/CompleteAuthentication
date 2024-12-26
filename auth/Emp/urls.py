from django.urls import path
from .views import EmployeeAPI
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Employee API",
        default_version='v1',
        description="Manage employee data",
        contact=openapi.Contact(email="contact@company.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),   
)
security=[  # Define the security scheme here for swagger
        {
            'Authorization': []
        }
    ]
# security_definition = {
#     'Token': {
#         'type': 'apiKey',
#         'in': 'header',
#         'name': 'Authorization'
#     }
# }
urlpatterns = [
    path('employee/', EmployeeAPI.as_view(), name='employee-list-create'),  # For listing and creating employees
    path('employee/<int:pk>/', EmployeeAPI.as_view(), name='employee-detail-update-delete'),  # For updating and deleting
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
