from django.contrib import admin
from .models import EmployeeData

@admin.register(EmployeeData)
class EmployeeAdmin(admin.ModelAdmin):
    list_display=['id','emp_id','emp_name','emp_email','department','description']