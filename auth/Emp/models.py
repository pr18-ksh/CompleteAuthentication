from django.db import models

class EmployeeData(models.Model):
    emp_id=models.IntegerField(unique=True)
    emp_name=models.CharField(max_length=255)
    emp_email=models.EmailField(unique=True)
    department = models.CharField(max_length=255)
    description= models.CharField(max_length=255)
    
    def _str_(self):
        return self.emp_name