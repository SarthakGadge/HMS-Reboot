from django.db import models
from userauth.models import Student
from rooms.models import Room, Bed
from userauth.models import Staff


class Issue(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE)
    description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Issue reported by {self.student} in {self.room}, Bed {self.bed}"
