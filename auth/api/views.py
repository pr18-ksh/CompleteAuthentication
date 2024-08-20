from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.hashers import make_password
from api.serializer import User, UserSerializer,LoginSerializer,ChangePasswordSerializer,ForgotPasswordSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth import get_user_model,login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sessions.models import Session
from auth import settings
import logging



# Configure the logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AuthView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        action = request.data.get('action')
        
        if action == 'register':
            return self.register_user(request)
        elif action == 'login':
            return self.login_user(request)
        elif action == 'change_password':
            return  self.change_password(request)
        elif action == 'forgot_password':
            return  self.forgot_password(request)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)     

    def register_user(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            # token, created = Token.objects.get_or_create(user=user)
            return Response({'message': "user created"}, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login_user(self, request):
        login_serializer = LoginSerializer(data=request.data)
        if login_serializer.is_valid():

            username = login_serializer.validated_data['username']
            password = login_serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'message':"Login sucessfully",'token': token.key}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
          
    def change_password(self, request):
        permission_classes = [IsAuthenticated]
        changepassword_serializer = ChangePasswordSerializer(data=request.data)
        
        if changepassword_serializer.is_valid():
            old_password = changepassword_serializer.validated_data['old_password']
            new_password = changepassword_serializer.validated_data['new_password']
            username = request.data.get('username')
            
            logging.debug(f"Received email: {username}")
            logging.debug(f"Received old password: {old_password}")
            logging.debug(f"Received new password: {new_password}")
            
            user = authenticate(request, username=username,password=old_password)

            if user:
                     user.set_password(new_password)
                     user.save()
                     login(request, user)
                     Token.objects.filter(user=user).delete()  # Delete old token
                     token, created = Token.objects.get_or_create(user=user)
                     logging.debug(f"Password changed successfully for: {user.username}")
                     return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
            else:
                     
                     return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)        
        return Response(changepassword_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def forgot_password(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email').lower().strip()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'No user with this email address'}, status=status.HTTP_400_BAD_REQUEST)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"http://127.0.0.1:8000/reset-password/{uid}/{token}/"

            # Send email (Make sure to configure email settings in Django settings)
            subject = 'Password Reset Request'
            message = render_to_string('password_reset_email.html', {
                'reset_link': reset_link
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordView(View):
    
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid link or expired'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return render(request, 'invalid_user.html', {'message': 'Invalid or expired token.'})

        if default_token_generator.check_token(user, token):
            context = {
                'uid': uidb64,
                'token': token
            }
            return render(request, 'password_reset_form.html', context)
        else:
            return Response({'error': 'Invalid link or expired'}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordConfirmView(APIView):   
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    User = get_user_model()
    
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            logger.debug(f"Attempting password reset for user: {user}")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid link or expired'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')  # Use request.data for DRF views
            if new_password:
                user.set_password(new_password)
                user.save()
                logger.debug(f"Password reset successful for user: {user}")
                
                # Authenticate the user with the new password
                user = authenticate(username=user.username, password=new_password)
                if user :
                    
                   login(request,user,backend='your.custom.backend')
                   logger.debug(f"User {user} logged in successfully after password reset")
                
                   Token.objects.filter(user=user).delete() 
                
                   # Optionally, generate a new token for the user (if using token-based auth)
                   token, created = Token.objects.get_or_create(user=user)
                   return Response({'token': token.key}, status=status.HTTP_200_OK)
                else:
                    # If authentication fails after password reset
                    return Response({'error': 'Failed to log in after password reset'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid link or expired'}, status=status.HTTP_400_BAD_REQUEST)




