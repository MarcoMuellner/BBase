# Generated by Django 2.2.3 on 2020-07-08 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_db', '0005_baseuser_enabled_value_card_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseuser',
            name='bingo_message',
            field=models.BooleanField(default=False, verbose_name='Received bingo message'),
        ),
    ]