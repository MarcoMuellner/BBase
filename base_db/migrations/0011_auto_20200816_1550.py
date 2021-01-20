# Generated by Django 2.2.3 on 2020-08-16 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_db', '0010_auto_20200803_0509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='error',
            name='cmd_string',
            field=models.CharField(max_length=1024, verbose_name='Command string that was executed'),
        ),
        migrations.AlterField(
            model_name='error',
            name='error',
            field=models.CharField(max_length=10000, verbose_name='Error string'),
        ),
        migrations.AlterField(
            model_name='error',
            name='error_type',
            field=models.CharField(max_length=256, verbose_name='Error type'),
        ),
    ]