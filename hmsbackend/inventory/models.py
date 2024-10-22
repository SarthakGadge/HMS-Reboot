from django.db import models
from userauth.models import Admin, Staff


class Inventory(models.Model):

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved'),
    ]

    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='not_approved')
    admin = models.ForeignKey(
        Admin, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)

    def __str__(self):
        return f"Inventory(description={self.description}, status={self.status})"
    


