import random
from django.shortcuts import render,redirect
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
import stripe
from django.conf import settings
import requests

stripe.api_key = settings.STRIPE_SECRET_KEY
# PAYPAL_


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
    



class CheckoutAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]
    lookup_field = "oid"
    queryset = api_models.CartOrder.objects.all()




class CouponApplyAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CouponSerializer
    permission_classes = [AllowAny]
    

    def create(Self,request,*args, **kwargs):
        order_id = request.data['order_id']
        coupon_code = request.data['coupon_code']
        
        order = api_models.CartOrder.objects.get(oid = order_id)
        coupon = api_models.Coupon.objects.get(code=coupon_code)

        if coupon:
            order_items = api_models.CartOrderItem.objects.filter(order=order)
            for item in order_items:
                if not coupon in item.coupons.all():
                    discount = item.total * coupon.discount / 100
                    item.total -= discount
                    item.price -= discount
                    item.saved -= discount
                    item.applied_coupon = True
                    item.coupons.add(coupon)
                
                    order.coupons.add(coupon)
                    order.total -= discount
                    order.sub_total -= discount
                    order.saved += discount
            
                    coupon.used_by.add(order.student)

                    order.save()
                    item.save()

                    return Response({"message":"Coupon activated"},status=status.HTTP_201_CREATED)
                    
                else:
                    return Response({"message":"Coupon already applied"},status=status.HTTP_200_OK)
                

            return Response({"message":"Coupon applied successfully"},status=status.HTTP_200_OK)
        else:
            return Response({"message":"Invalid coupon code"},status=status.HTTP_404_NOT_FOUND)
        



class StripeCheckoutAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]


    def create(self,request,*args,**kwargs):
        order_oid = self.kwargs['order_oid']
        order = api_models.CartOrder.objects.get(oid=order_oid)


        if not order:
            return Response({"message":"order not found"},status=status.HTTP_404_NOT_FOUND)
        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email = order.email,
                payment_method_types = ['card'],
                line_items=[
                    {
                        'price_data':{
                            'currency':'usd',
                            'product_data':{
                                'name': order.full_name,
                            },
                            'unit_amount':int(order.total * 100)
                        },
                        'quantity':1,
                    },
                    

                ],
                mode='payment',
                success_url = settings.FRONTEND_SITE_URL + 'payment-success/' + order.oid + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url = settings.FRONTEND_SITE_URL + 'payment-failed/'
            )
            print("Checkout session === ",checkout_session)
            order.stripe_session_id = checkout_session.id

            return redirect(checkout_session.url)
        except stripe.error.StripeError as e:
            return Response({"message": f"Something went wrong with payment. Error {str(e)}"})


def get_access_token(client_id,secret_key):
    token_url = "https://api.sandbox.paypal.com/v1/oauth/token"
    data = {'grant_type':'client_credentials'}
    auth = (client_id,secret_key)
    response = requests.post(token_url,data=data,auth=auth)


    if response.status_code == 200:
        print("Access Token response : ",response.json()['access_token'])
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get access token from paypal: {response.status_code}")


class PaymentSuccessAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = api_models.CartOrder.objects.all()

    def create(self, request, *args, **kwargs):
        order_oid = request.data['order_oid']
        session_id = request.data['session_id']
        # paypal_order_id = request.data['paypal_order_id']

        order = api_models.CartOrder.objects.get(oid=order_oid)
        order_items = api_models.CartOrderItem.objects.filter(order=order)

        # paypal payment 
        # if paypal_order_id!="null":
        #     paypal_api_url = f"https://api-m.sandbox.com/v2/checkout/orders/{paypal_order_id}"
        #     header = {
        #         "Content-Type": "application/json",
        #         "Authorization": f"Bearer {get_access_token(settings.PAYPAL_CLIENT_ID,settings.PAYPAL_SECRET_KEY)}"
        #     }

        # Stripe payment success
        if session_id != 'null':
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                if order.payment_status == "Processing":
                    order.payment_status = "Paid"
                    order.save()

                    api_models.Notification.objects.create(user=order.student, order=order, type="Course Enrollment Completed")
                    for o in order_items:
                        api_models.Notification.objects.create(teacher=o.teacher, order=order, order_item=o, type="New Order")
                        api_models.EnrolledCourse.objects.create(course=o.course, user=order.student, teacher=o.teacher, order_item=o)

                    return Response({"message": "Payment Successful"})
                else:
                    return Response({"message": "Already Paid"})
            else:
                    return Response({"message": "Payment Failed"})
            


class SearchCourseAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        query = self.request.GET.get('query')
        return api_models.Course.objects.filter(title__icontains=query,platform_status='Published',teacher_course_status='Published')
    



