import random
import datetime
from django.core.mail import send_mail
from django.utils import timezone
from django.db import connection


def generate_and_send_otp(user):
    otp = str(random.randint(1000, 9999))

    # Save OTP in the user model or OTP table
    user.otp = otp
    user.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
    user.max_otp_try -= 1
    if user.max_otp_try == 0:
        user.otp_max_out = timezone.now() + timezone.timedelta(hours=1)
    user.save()

    subject = 'Verify Your Email'
    message = f'''
Subject: Verify Your Email
Dear {user.username},
You have registered a new account. Please use the following One-Time Password (OTP) to verify your email:
OTP: {otp}
Note: Do not share this OTP with anyone.
If you did not register this account, please ignore this email.
Thank you,
    '''

    from_email = "aa@thedatatechlabs.com"
    to_email = [user.email]

    try:
        send_mail(subject, message, from_email, to_email, fail_silently=False)
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

    return True
