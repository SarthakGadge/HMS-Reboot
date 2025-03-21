# Generated by Django 4.1.7 on 2024-10-23 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_inventory_admin_inventory_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='category',
            field=models.CharField(default='wires', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventory',
            name='price',
            field=models.IntegerField(default=1500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventory',
            name='quantity',
            field=models.IntegerField(default=12),
            preserve_default=False,
        ),
    ]
