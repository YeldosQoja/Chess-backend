# Generated by Django 5.0.6 on 2024-09-01 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess', '0018_friendrequest_is_accepted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='finished_at',
            field=models.DateTimeField(null=True),
        ),
    ]
