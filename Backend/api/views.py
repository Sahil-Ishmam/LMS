import random
from django.shortcuts import render
from api import serializer as api_serializer
from rest_framework_simplejwt.views import TokenObtainPairView
# Create your views here.
from rest_framework import generics,status
from userauths.models import User,Profile
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    # both user authencticate and not authenticated user can access this
    serializer_class = api_serializer.RegisterSerializer

def generate_random_otp(length=6):
    otp = "".join([str(random.randint(0,9)) for _ in range(length)])
    return otp




class PasswordResetEmailVerifyAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs['email'] # api/v1/password-email-verify/example@gmail.com/
        user = User.objects.filter(email=email).first()

        if user:
            uuidb64 = user.id
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh.access_token)

            user.refresh_token = refresh_token
            user.otp = generate_random_otp()
            user.save()
            
            
            link = f"http://localhost:5173/create-new-password/?otp={user.otp}&uuidb64={uuidb64}&refresh_token={refresh_token}"

            print("link == ",link)
        
        return user
    
class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        payload = request.data

        otp = payload['otp']
        uuidb64 = payload['uuidb64']
        password = payload['password']

        user = User.objects.get(id=uuidb64,otp=otp)

        if user:
            user.set_password(password)
            user.otp = ""
            user.save()

            return Response({"message":"Password changed successfully"},status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"User Doesn't Exists"},status=status.HTTP_404_NOT_FOUND)
        

