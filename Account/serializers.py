from rest_framework import serializers
from Account.models import CustomUser
from Account.utils import send_verification_email
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, force_str, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

import re

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'phone_number',
            'university_id',
            'applied_for',
            #'user_type',
            #'is_varified'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        """
        Ensure the email ends with @nub.ac.bd
        """
        if not value.lower().endswith('@nub.ac.bd'):
            raise serializers.ValidationError("Email must end with '@nub.ac.bd'")
        return value

    def detect_user_type_from_email(self, email):
        """
        Determine if user is Student or Teacher based on the email format.
        Student emails typically contain a numeric ID.
        
        Student example: sharif_41220100032@nub.ac.bd
        Teacher example: shiam@nub.ac.bd
        """
        # Regex to check for a sequence of 10+ digits in the local part of the email
        match = re.search(r'\d{6,}', email.split('@')[0])
        
        if match:
            return "Student"
        else:
            return "Teacher"

    def create(self, validated_data):
        request = self.context.get('request')  # needed to build absolute URI
        email = validated_data['email']
        user_type = self.detect_user_type_from_email(email)
        password = validated_data.pop('password')  # extract password safely

        user = CustomUser(
            email=email,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            university_id=validated_data.get('university_id'),
            applied_for=validated_data.get('applied_for', ''),
            user_type=user_type,
        )
        user.set_password(password)
        user.save()

        send_verification_email(user, request)
        return user
        

class SignUpRequestSerializer (serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'phone_number',
            'university_id',
            'applied_for',
            #'user_type',
            #'is_varified'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def create(self, validated_data):
        request = self.context.get('request')  # needed to build absolute URI
        email = validated_data['email']
        password = validated_data.pop('password')  # extract password safely

        user = CustomUser(
            email=email,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            university_id=validated_data.get('university_id'),
            applied_for=validated_data.get('applied_for', ''),
            is_active=False
        )
        user.set_password(password)
        user.save()

        send_verification_email(user, request)
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_new_password = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)
    
    
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
