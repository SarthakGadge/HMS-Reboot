# Generated by Django 4.1.7 on 2024-10-09 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_delete_roomcheckinstud'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
