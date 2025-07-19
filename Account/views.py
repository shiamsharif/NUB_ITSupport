from django.shortcuts import render
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from Account.serializers import CustomUserSerializer, SignUpRequestSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import PasswordResetRequestSerializer, PasswordResetRequestSerializer, SendOTPSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from Account.utils import send_otp_on_mail
from django.utils import timezone
from django.shortcuts import get_object_or_404 
from .models import EmailVerificationToken
    
User = get_user_model()


class UniversityEmailSignupView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})  
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=201)
        return Response(serializer.errors, status=400)
    
class GeneralSignupView(APIView): 
    permission_classes = [AllowAny]
    serializer_class = SignUpRequestSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully. Please check your email to verify your account."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            
            email_varification_token = EmailVerificationToken.objects.filter(user=user, token=token).first()
            if not email_varification_token:
                return Response({'error': 'Invalid verification token'}, status=status.HTTP_400_BAD_REQUEST)

            if default_token_generator.check_token(user, token):
                user.is_varified = True
                if not user.email.lower().endswith('@nub.ac.bd'):
                    user.is_active = False  # Deactivate user if email is not from NUB
                else:
                    user.is_active = True
                
                user.save()
                email_varification_token.delete()
                return Response({'message': 'Email successfully verified.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid UID'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")
        

        # Check if user is active
        if not user.is_active:
            return Response({"error": "User account is inactive"}, status=status.HTTP_403_FORBIDDEN)
        
        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        
        if not User.objects.filter(email=email).exists():
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(email=email)
        
        # check if user is verified
        if not user.is_varified:
            return Response({"error": "Email is not verified"}, status=status.HTTP_403_FORBIDDEN)

        # check password
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })
        
        
class PasswordResetView(APIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        
        new_password = request.data.get('new_password')
        confirm_new_password = request.data.get('confirm_new_password')
        
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_new_password:
            return Response({"error": "New password and confirm password do not match"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
    
    
    
# email -> one time code 


# email, one time code , new password, confirm new password


class SendOTP(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            if not User.objects.filter(email=email).exists():
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
            # Generate and send one-time code logic here
            
            send_otp_on_mail(email)
            # For example, you can use Django's built-in email functionality to send the code
            
            return Response({"message": "One-time code sent to your email"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ForgetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        confirm_new_password = request.data.get('confirm_new_password')

        user = get_object_or_404(User, email=email)

        # Check if all fields are provided
        if not all([email, otp, new_password, confirm_new_password]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        # Check if OTP is valid
        if not user.otp or user.otp != otp:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP expired (older than 5 minutes)
        if not user.otp_generated_at or (timezone.now() - user.otp_generated_at).total_seconds() > 300:
            return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Check password match
        if new_password != confirm_new_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        # Update password
        user.set_password(new_password)
        user.otp = None
        user.otp_generated_at = None
        user.save()

        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)



    