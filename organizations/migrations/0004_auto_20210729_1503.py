# Generated by Django 3.2.4 on 2021-07-29 21:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_user_favorites'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Favorites',
        ),
        migrations.DeleteModel(
            name='Favorites2',
        ),
    ]