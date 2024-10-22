from django.db import models
from userauth.models import Admin, Student
from hostel.models import Hostel
from django.core.exceptions import ValidationError


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# class Room(models.Model):
#     admin_id = models.ForeignKey(Admin, on_delete=models.CASCADE)
#     hostel = models.ForeignKey(
#         Hostel, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
#     room_number = models.IntegerField()
#     floor_number = models.IntegerField()
#     rent = models.IntegerField()
#     room_image = models.ImageField(blank=True, null=True)
#     date = models.DateField(auto_now_add=True, blank=True, null=True)
#     occupancy = models.IntegerField()
#     vacancy = models.IntegerField()
#     amenities = models.ManyToManyField(Amenity, related_name='rooms')

#     def clean(self):
#         # Check if a room with the same room number exists on the same floor
#         if Room.objects.filter(
#             hostel=self.hostel,
#             floor_number=self.floor_number,
#             room_number=self.room_number
#         ).exclude(pk=self.pk).exists():
#             raise ValidationError(
#                 f"Room number {self.room_number} already exists on floor {self.floor_number} of hostel {self.hostel}."
#             )

#     def save(self, *args, **kwargs):
#         try:
#             # Call clean() method to validate before saving
#             self.clean()
#             super().save(*args, **kwargs)

#         except ValidationError as e:
#             # Handle the validation error gracefully by raising it
#             raise e

#         # Your bed handling logic remains unchanged
#         creating_new = self.pk is None
#         if not creating_new:
#             previous_room = Room.objects.get(pk=self.pk)
#             previous_vacancy = previous_room.vacancy
#         else:
#             previous_vacancy = 0

#         current_beds = Bed.objects.filter(room=self).count()

#         if creating_new:
#             for _ in range(self.vacancy):
#                 Bed.objects.create(
#                     room=self,
#                     status='available',
#                     checkIn_date=None,
#                     checkOut_date=None,
#                     student=None
#                 )
#         else:
#             if self.vacancy > previous_vacancy:
#                 for _ in range(self.vacancy - previous_vacancy):
#                     Bed.objects.create(
#                         room=self,
#                         status='available',
#                         checkIn_date=None,
#                         checkOut_date=None,
#                         student=None
#                     )
#             elif self.vacancy < previous_vacancy:
#                 beds_to_remove = Bed.objects.filter(
#                     room=self, student__isnull=True)

#                 beds_to_remove = beds_to_remove[:
#                                                 previous_vacancy - self.vacancy]

#                 for bed in beds_to_remove:
#                     bed.delete()

#     def __str__(self):
#         return f"Room {self.room_number} on Floor {self.floor_number}"


class Room(models.Model):
    admin_id = models.ForeignKey(Admin, on_delete=models.CASCADE)
    hostel = models.ForeignKey(
        Hostel, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    room_number = models.IntegerField()
    floor_number = models.IntegerField()
    rent = models.IntegerField()
    room_image = models.ImageField(blank=True, null=True)
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    occupancy = models.IntegerField()
    vacancy = models.IntegerField()
    amenities = models.ManyToManyField(Amenity, related_name='rooms')

    def save(self, *args, **kwargs):
        creating_new = self.pk is None

        if not creating_new:
            previous_room = Room.objects.get(pk=self.pk)
            previous_vacancy = previous_room.vacancy
        else:
            previous_vacancy = 0

        super().save(*args, **kwargs)

        current_beds = Bed.objects.filter(room=self).count()

        if creating_new:
            # Create beds if this is a new room
            for _ in range(self.vacancy):
                Bed.objects.create(
                    room=self,
                    status='available',
                    checkIn_date=None,
                    checkOut_date=None,
                    student=None
                )
        else:
            if self.vacancy > previous_vacancy:
                # Create additional beds if vacancy increased
                for _ in range(self.vacancy - previous_vacancy):
                    Bed.objects.create(
                        room=self,
                        status='available',
                        checkIn_date=None,
                        checkOut_date=None,
                        student=None
                    )
            elif self.vacancy < previous_vacancy:
                # Decrease the number of beds if vacancy decreased
                beds_to_remove = Bed.objects.filter(
                    room=self, student__isnull=True)

                # Delete only the number of beds that need to be removed
                beds_to_remove = beds_to_remove[:
                                                previous_vacancy - self.vacancy]

                for bed in beds_to_remove:
                    bed.delete()  # Delete each bed individually

    def __str__(self):
        return f"Room {self.room_number} on Floor {self.floor_number}"


class Bed(models.Model):
    BED_AVAILABILITY = [
        ('available', 'available'),
        ('unavailable', 'unavailable')
    ]

    BED_DURATION = [
        (3, 3),
        (6, 6),
        (9, 9)
    ]

    checkIn_date = models.DateField(null=True, blank=True)
    checkOut_date = models.DateField(null=True, blank=True)
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(choices=BED_AVAILABILITY,
                              max_length=50, default='available')
    duration = models.IntegerField(choices=BED_DURATION, null=True, blank=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Bed in Room {self.room} - {self.status}"


# class RoomBooking(models.Model):

#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     booking_date = models.DateField(auto_now_add=True)
#     check_in_date = models.DateField()
#     check_out_date = models.DateField()

#     def __str__(self):
#         return f"Booking: Room {self.room.room_number} for {self.student}"
