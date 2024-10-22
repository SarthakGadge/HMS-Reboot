from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from userauth.models import CustomUser, Superadmin


class Command(BaseCommand):
    help = 'Create a Superadmin user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str,
                            help='Username for the superadmin')
        parser.add_argument('email', type=str, help='Email for the superadmin')
        parser.add_argument('password', type=str,
                            help='Password for the superadmin')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password']

        if Superadmin.objects.exists():
            self.stdout.write(self.style.ERROR('A Superadmin already exists.'))
            return

        # Create a new user
        user = CustomUser(
            username=username,
            email=email,
            role='superadmin'  # Set the role to superadmin
        )
        user.password = make_password(password)  # Hash the password
        user.save()

        # Create a Superadmin instance
        superadmin = Superadmin(user=user)
        superadmin.save()

        self.stdout.write(self.style.SUCCESS(
            f'Superadmin created: {username}'))
