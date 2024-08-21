from rest_framework import serializers
from .models import EmployeeData

class EmpSerializer(serializers.ModelSerializer):
    class Meta:
        model=EmployeeData
        fields=['id','emp_id','emp_name','emp_email','department','description']