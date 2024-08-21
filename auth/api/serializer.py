from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.models import CustomUser

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    mobile_number =serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['id','first_name', 'last_name', 'username', 'email', 'password','mobile_number']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            mobile_number=validated_data['mobile_number']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField(write_only=True)
    new_password=serializers.CharField(write_only=True)
    username = serializers.CharField()
class ForgotPasswordSerializer(serializers.Serializer):
     email = serializers.EmailField()
