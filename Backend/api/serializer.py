from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from userauths.models import Profile,User
from django.contrib.auth.password_validation import validate_password
from api import models as api_models


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['full_name'] = user.full_name
        # ...

        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['full_name','email','password','password2']
    
    def validate(self,attr):
        if attr['password'] != attr['password2']:
            raise serializers.ValidationError({"Password":"Password fields didn't match"})
        return attr

    def create(self, validated_data):
        user = User.objects.create(
            full_name = validated_data['full_name'],
            email = validated_data['email'],
        )

        email_username,_ = user.email.split("@")
        user.username = email_username
        user.set_password(validated_data['password'])
        user.save()

        return user
    

class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        fields = [
            "user",
            "image",
            "full_name",
            "bio",
            "facebook",
            "twitter",
            "linkedin",
            "about",
            "country",
            "students",
            "courses",
            "review",
        ]
        model = api_models.Teacher


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['title','image','slug','course_count']
        model = api_models.Category



class VariantItemSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.VariantItem


class VariantSerializer(serializers.ModelSerializer):
    variant_items = VariantItemSerializer(many=True)
    class Meta:
        fields = '__all__'
        model = api_models.Variant





class Question_Answer_MessageSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(many=False)

    class Meta:
        fields = '__all__'
        model = api_models.Question_Answer_Message


class Question_AnswerSerializer(serializers.ModelSerializer):
    messages = Question_Answer_MessageSerializer(many=True)
    profile = ProfileSerializer(many=False)

    class Meta:
        fields = '__all__'
        model = api_models.Question_Answer



class CartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Cart


class CartOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.CartOrderItem


class CartOrderSerializer(serializers.ModelSerializer):
    order_items = CartOrderItemSerializer(many=True)

    class Meta:
        fields = '__all__'
        model = api_models.CartOrder





class CertificateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Certificate


class CertificateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Certificate
        

class CompletedLessonSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.CompletedLesson


class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Note

class ReviewSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        fields = '__all__'
        model = api_models.Review

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Notification

class CouponSerializer(serializers.ModelSerializer):


    class Meta:
        fields = '__all__'
        model = api_models.Coupon



class WishListSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.WishList




class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Country



class EnrolledCourseSerializer(serializers.ModelSerializer):
    lectures = VariantItemSerializer(many=True,read_only=True)
    completed_lesson = CompletedLessonSerializer(many=True,read_only=True)
    curriculum = VariantItemSerializer(many=True,read_only=True)
    note = NoteSerializer(many=True,read_only=True)
    question_answer = Question_AnswerSerializer(many=True,read_only=True)
    review = ReviewSerializer(many=True,read_only=True)

    class Meta:
        fields = '__all__'
        model = api_models.EnrolledCourse



class CourseSerializer(serializers.ModelSerializer):
    students = EnrolledCourseSerializer(many=True)
    curriculum = VariantItemSerializer(many=True)
    lectures = VariantItemSerializer(many=True)


    class Meta:
        fields = [
            "category",
            "teacher",
            "file",
            "image",
            "title",
            "description",
            "price",
            "language",
            "level",
            "platform_status",
            "teacher_course_status",
            "course_id",
            "slug",
            "date",
            "students",
            "curriculum",
            "lectures",
            "average_rating",
            "rating_count",
            "reviews",
        ]
        model = api_models.Course

