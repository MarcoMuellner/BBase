# Generated by Django 2.2.3 on 2020-05-23 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_db', '0004_auto_20200522_0210'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseuser',
            name='enabled_value_card_until',
            field=models.DateTimeField(default=None, null=True, verbose_name='Value card enabled until'),
        ),
    ]
