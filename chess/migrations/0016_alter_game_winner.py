# Generated by Django 5.0.6 on 2024-07-21 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess', '0015_alter_game_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='winner',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
