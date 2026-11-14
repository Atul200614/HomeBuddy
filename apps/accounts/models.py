from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Primary user model for HomeBuddy.

    Roles:
      CUSTOMER — books services
      PROVIDER — verified technician who fulfils bookings
      ADMIN    — platform operator
    """

    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('PROVIDER', 'Service Provider'),
        ('ADMIN', 'Platform Administrator'),
    )

    email = models.EmailField(unique=True, verbose_name="Email Address")
    phone = models.CharField(
        max_length=15, unique=True, null=True, blank=True, verbose_name="Mobile Number"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER', verbose_name="User Role")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Profile Picture")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Last Login IP")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User Account'
        verbose_name_plural = 'User Accounts'
        ordering = ['-date_joined']
        indexes = [models.Index(fields=['role', 'is_active'])]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        # Keep username aligned with email so authenticate() stays predictable.
        if self.email:
            self.email = self.email.strip().lower()
        if not self.username and self.email:
            self.username = self.email
        elif self.username:
            self.username = self.username.strip()
            if '@' in self.username or (self.email and self.username.lower() == self.email):
                self.username = self.username.lower()
        super().save(*args, **kwargs)

    @property
    def is_customer(self):
        return self.role == 'CUSTOMER'

    @property
    def is_provider(self):
        return self.role == 'PROVIDER'

    @property
    def is_admin_user(self):
        return self.role == 'ADMIN' or self.is_superuser

    @property
    def display_name(self):
        return self.get_full_name() or self.username
