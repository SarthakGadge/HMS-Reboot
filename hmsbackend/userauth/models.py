from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from hostel.models import Hostel


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('superadmin', 'Superadmin'),
    )

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)  # Make sure email is unique
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    max_otp_try = models.IntegerField(default=3)
    otp_max_out = models.DateTimeField(null=True, blank=True)
    password_reset_otp = models.CharField(max_length=6, null=True, blank=True)
    password_reset_otp_expiry = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'  # Use email as the username field
    REQUIRED_FIELDS = ['username']  # Remove email from here if it was present

    def __str__(self):
        return self.email

    def is_otp_valid(self):
        if self.otp and self.otp_expiry:
            return timezone.now() <= self.otp_expiry
        return False

    def can_send_otp(self):
        if self.otp_max_out:
            return timezone.now() > self.otp_max_out
        return self.max_otp_try > 0


class Superadmin(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if Superadmin.objects.exists() and not self.pk:
            raise ValueError('There can only be one Superadmin instance.')
        super(Superadmin, self).save(*args, **kwargs)

    def __str__(self):
        return f"Superadmin: {self.user.username}"


class Admin(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile')
    hostel = models.ForeignKey(
        Hostel, on_delete=models.CASCADE, related_name='admins')
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='admin_photo/', blank=True, null=True)
    gender = models.CharField(max_length=20,
                              choices=[
                                  ('male', 'male'),
                                  ('female', 'female')
                              ]
                              )

    def __str__(self):
        return f"{self.user.username} - Admin"

    class Meta:
        db_table = 'admin'


class Staff(models.Model):
    DP_CHOICES = (
        ('security', 'security'),
        ('staff', 'staff'),
        ('maintenance', 'maintenance'),
        ('inventory', 'inventory'),
    )

    SHIFT_CHOICES = (
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('night', 'Night'),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    hostel = models.ForeignKey(
        Hostel, on_delete=models.CASCADE, related_name='staff')
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='created_staff')
    name = models.CharField(max_length=20)
    shift = models.CharField(
        max_length=20, choices=SHIFT_CHOICES, default='morning')
    Department = models.CharField(
        max_length=20, choices=DP_CHOICES, default='staff')
    contact = models.CharField(max_length=15)
    photo = models.ImageField(
        upload_to='staff_photos/', blank=True, null=True)
    gender = models.CharField(max_length=20,
                              choices=[
                                  ('male', 'male'),
                                  ('female', 'female')
                              ]
                              )
    # Photo field to be added

    def __str__(self):
        return f"{self.user.username} - Staff"

    class Meta:
        db_table = 'staff'


class Student(models.Model):
    G_CHOICES = (
        ('male', 'male'),
        ('female', 'female'),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student')
    hostel = models.ForeignKey(
        Hostel, on_delete=models.CASCADE, related_name='student')
    name = models.CharField(max_length=150)
    dob = models.DateField()
    contact = models.CharField(max_length=15)
    nationality = models.CharField(max_length=15)
    gender = models.CharField(
        max_length=20, choices=G_CHOICES)
    guardian_name = models.CharField(max_length=100)
    guardian_contact = models.CharField(max_length=15)
    photo = models.ImageField(
        upload_to='student_photos/', blank=True, null=True)
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='created_student')

    def __str__(self):
        return f"{self.user.username} - Student"

    class Meta:
        db_table = 'student'
