from django.shortcuts import render
from django.conf import settings

# django validations and auth methods
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import check_password

# rest framework dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.permissions import IsAuthenticated

# swagger documentation libs
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# other requirements
import datetime, environ, os

# models, serializers and other dependencies
from django.contrib.auth.models import User
from .serializers import UserSerializer, ProfileSerializer

env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))


def getUserByEmail(email:str) -> User|AuthenticationFailed:
    """
    returns User if there is any user with provided email or raise AuthenticationFailed (401)

    params:
    email : user provided email as str
    """
    user = User.objects.filter(email=email).first()
    if user is None:
        raise AuthenticationFailed("User not found!")
    return user

def getUserByID(payload:dict) -> User|NotFound :
    """
    Returns User with the id provided in payload.

    If there is no User with the ID the raise NotFound (404)

    params:
        payload : Decoded JWT Token as a dict {'id', 'exp', 'iat'}
    """
    user = User.objects.filter(id=payload["id"]).first()
    if not user:
        raise NotFound("User is not found!")
    return user

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        profile_data = data.pop('profile')

        # check if the user data is valid
        if User.objects.filter(username=data['username']).exists():
            return Response(
                    {'error': 'Username already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=data['email']).exists():
            return Response(
                    {'error': 'Email already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST)
        
        try:
            serializer = UserSerializer(data = data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()     

            profile_data['user'] = user.id
            profile_serializer = ProfileSerializer(data = profile_data)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
            
        except DjangoValidationError as e:
            return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {           'message': 'User created successfully'}, 
                        status=status.HTTP_201_CREATED
                        )
    

class LoginView(APIView):
    def post(self, request):

        username = request.data['username']
        password = request.data['password']

        django_user = authenticate(request=request, username=username, password=password) 
        print( "auth")
        login(request=request, user=django_user)
        print("login")


        return Response(
                {'message': 'User logged in successfully'}, 
                status=status.HTTP_200_OK)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        logout(request=request)
        return Response(
                {'message': 'User logged out successfully'}, 
                status=status.HTTP_200_OK)
    

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        profile_serializer = ProfileSerializer(user.profile)
        result = user_serializer.data | profile_serializer.data
        return Response(
                        result,
                        status=status.HTTP_200_OK)
    
    def delete(self, request):
        user = request.user
        user.delete()
        return Response(
                {'message': 'User deleted successfully'}, 
                status=status.HTTP_200_OK)
