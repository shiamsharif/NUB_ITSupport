from django.contrib import admin
from .models import CustomUser, EmailVerificationToken

admin.site.register(CustomUser)
admin.site.register(EmailVerificationToken)