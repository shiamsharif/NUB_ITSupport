import random
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from Main import settings
from .models import EmailVerificationToken


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


User = get_user_model()

def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))  # safely encode user ID
    
    EmailVerificationToken.objects.create(
        user=user,
        token=token,
    )

    verify_url = request.build_absolute_uri(
        reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token})
    )
    
    subject = 'Verify your email address'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    # Render HTML email
    html_message = render_to_string('emails/verify_email.html', {
        
        'verify_url': verify_url,
    })

    # Fallback plain text
    plain_message = f'Hi {user.username}, please click the link to verify your email: {verify_url}'

    email = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()



    
def send_otp_on_mail(email):
    user = User.objects.get(email=email)
    otp = str(random.randint(100000, 999999))  # Generate a random 6-digit OTP
    user.otp = otp
    user.otp_generated_at = timezone.now()
    user.save()

    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp}'
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    
    return otp