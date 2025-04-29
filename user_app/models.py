from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

PLAN_ATTEMPTS = {
    "basic": 5, 
    "pro": 10,   
    "premium": 50  
}
class Userinfo(AbstractUser):
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True) 
    email = models.EmailField(max_length=50, unique=True, null=True, blank=True)
    recent_searches = models.JSONField(null=True, blank=True, help_text="Stores recent searches for AI suggestions.")
    attempt = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=40, unique=True, null=True, blank=True)

    membership_type = models.CharField(
        max_length=20, 
        null=True, 
        blank=True
    )
    
    registration_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Provide unique related_name for groups
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # Provide unique related_name for permissions
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    def save(self, *args, **kwargs):
        if self.membership_type and (self.attempt is None or self.attempt == 0):
            self.attempt = PLAN_ATTEMPTS.get(self.membership_type, 0)
        super().save(*args, **kwargs)


class Payment(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]
    
    BASIC = 'basic'
    PRO = 'pro'
    PREMIUM = 'premium'
    
    PLAN_CHOICES = [
        (BASIC, 'Basic'),
        (PRO, 'Pro'),
        (PREMIUM, 'Premium'),
    ]
    
    PLAN_PRICES = {
        BASIC: 499,
        PRO: 999,
        PREMIUM: 1499
    }

    user = models.ForeignKey('Userinfo', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    method = models.CharField(max_length=20, default='card')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    order_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=BASIC)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} - {self.status} - {self.plan}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == self.COMPLETED:
            plan_type = self.plan
            if plan_type in PLAN_ATTEMPTS:
                self.user.membership_type = plan_type
                self.user.attempt = PLAN_ATTEMPTS[plan_type]
                self.user.save()

