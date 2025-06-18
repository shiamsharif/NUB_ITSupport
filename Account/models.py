
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


USER_TYPE = {
    "Teacher": "Teacher",
    "Student": "Student",
    "Staff": "Staff",
    "ItStaff": "ItStaff",
}
class CustomUserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    # username= models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    university_id = models.CharField(max_length=15, blank=True)
    applied_for = models.CharField(max_length=20, choices=USER_TYPE.items(), blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE.items(), blank=True, null=True)
    is_varified = models.BooleanField(default=False)
    
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    otp = models.CharField(max_length=10, blank=True, null=True)
    otp_generated_at = models.DateTimeField(blank=True, null=True)


    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
        
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

