import random
from django.shortcuts import render
from api import serializer as api_serializer
from rest_framework_simplejwt.views import TokenObtainPairView
# Create your views here.
from rest_framework import generics,status
from userauths.models import User,Profile
from api  import models as api_models



from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from decimal import Decimal


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
        

class CategoryListAPIView(generics.ListAPIView):
    queryset = api_models.Category.objects.filter(active=True)  
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]


class CourseListAPIView(generics.ListAPIView):
    queryset = api_models.Course.objects.filter(platform_status="Published", teacher_course_status="Published")
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]



class CourseDetailAPIView(generics.RetrieveAPIView):
    
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]
    queryset = api_models.Course.objects.filter(platform_status="Published", teacher_course_status="Published")

    def get_object(self):
        slug = self.kwargs['slug']
        course = api_models.Course.objects.get(slug=slug,platform_status="Published", teacher_course_status="Published")
        return course
    

class CartAPIView(generics.CreateAPIView):
    queryset = api_models.Cart.objects.all()
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]


    def create(self,request,*args, **kwargs):
        course_id = request.data['course_id']
        user_id = request.data['user_id']
        price = request.data['price']
        country_name = request.data['country_name']
        cart_id = request.data['cart_id']


        course = api_models.Course.objects.filter(id=course_id).first()
        
        if(user_id !='undefined'):
            user = User.objects.filter(id=user_id).first()
        else:
            user = None
        
        try:
            country_object = api_models.Country.objects.filter(name=country_name).first()
            country = country_object.name
        except:
            country_object = None
            country = "Bangladesh"

        if country_object:
            tax_rate =  country_object.tax_rate / 100
        else:
            tax_rate = 0
        

        cart = api_models.Cart.objects.filter(id=cart_id,course=course).first()

        if cart:
            cart.course = course
            cart.user = user
            cart.price = price
            cart.country = country
            cart.tax_fee = Decimal(price) * Decimal(tax_rate)
            cart.cart_id = cart_id
            cart.total = Decimal(cart.price) + Decimal(cart.tax_fee)
            cart.save()

            return Response({"message":"Cart updated successfully"},status=status.HTTP_200_OK)
        else:
            cart = api_models.Cart()
            cart.course = course
            cart.user = user
            cart.price = price
            cart.country = country
            cart.tax_fee = Decimal(price) * Decimal(tax_rate)
            cart.cart_id = cart_id
            cart.total = Decimal(cart.price) + Decimal(cart.tax_fee)
            cart.save()

            return Response({"message":"Cart created successfully"},status=status.HTTP_201_CREATED)
        

    
class CartListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        cart_id = self.kwargs['cart_id'] 
        queryset = api_models.Cart.objects.filter(cart_id=cart_id)
        return queryset 

class CartItemDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']

        return api_models.Cart.objects.filter(cart_id=cart_id,id=item_id).first()
    
class CartStatsAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    lookup_field = 'cart_id'


    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = api_models.Cart.objects.filter(cart_id=cart_id)
        return queryset
    
    def get(self,request,*args, **kwargs):
        queryset = self.get_queryset()
        
        total_price = 0.00
        total_tax = 0.00
        total_total = 0.00



        for cart_item in queryset:
            total_price += float(cart_item.price)
            total_tax += float(cart_item.tax_fee)
            total_total += round(float(cart_item.total),2)

        
        data = {
            "price" : total_price,
            "tax" : total_tax,
            "total" : total_total
        }

        return Response(data,status=status.HTTP_200_OK)

    


class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = api_models.CartOrder.objects.all()


    def create(self,request, *args, **kwargs):
        full_name = request.data['full_name']
        email = request.data['email']
        country = request.data['country']
        cart_id = request.data['cart_id']
        user_id = request.data['user_id']



        if user_id != 0:
            # user = User.objects.filter(id=user_id)
            user = User.objects.filter(id=user_id).first()
        else:
            user = None

        cart_items = api_models.Cart.objects.filter(cart_id=cart_id)

        total_price = Decimal(0.00)
        total_tax = Decimal(0.00)
        total_initial_total = Decimal(0.00)
        total_total = Decimal(0.00)


        order = api_models.CartOrder.objects.create(
            full_name=full_name,
            email = email,
            country = country,
            student = user,
        )

        for item in cart_items:
            api_models.CartOrderItem.objects.create(
                order = order,
                course = item.course,
                price = item.price,
                tax_fee = item.tax_fee,
                total = item.total,
                initial_total = item.initial_total,
                teacher = item.course.teacher
            )

            total_price += Decimal(item.price)
            total_tax += Decimal(item.tax_fee)
            total_initial_total += Decimal(item.initial_total)
            total_total += Decimal(item.total)

            order.teachers.add(item.course.teacher)

        order.sub_total = total_price
        order.tax_fee = total_tax
        order.initial_total = total_initial_total
        order.total = total_total

        order.save()


        return Response({"message":"Order created successfully"},status=status.HTTP_201_CREATED)
    




        





