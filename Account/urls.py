from django.urls import path
from .views import UniversityEmailSignupView, GeneralSignupView, EmailVerifyView, LoginView, PasswordResetView, SendOTP, ForgetPasswordView, ProfileView, ItStaffCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    #Registration
    path('signup/university/', UniversityEmailSignupView.as_view(), name='university-signup'),
    # SignUp Request
    path('signup/general/', GeneralSignupView.as_view(), name='general-signup'),
    # Mail verification
    path('verify-email/<uidb64>/<token>/', EmailVerifyView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),    
    # Reset password
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    # Forget password
    path('send-otp/', SendOTP.as_view(), name='send_otp'),
    path('forgot-password/', ForgetPasswordView.as_view(), name='forget_password'),
    
    #Profile:
    path("me/profile/", ProfileView.as_view(), name="profile"),
    
    #Create ITStaff
    path("itstaff/", ItStaffCreateView.as_view(), name="itstaff-create"),


]
