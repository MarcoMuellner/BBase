# Generated by Django 2.2.3 on 2020-09-15 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_db', '0013_auto_20200817_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseguild',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False, verbose_name='Guild id, discord'),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='d_id',
            field=models.BigIntegerField(verbose_name='User id, discord'),
        ),
        migrations.AlterField(
            model_name='userignore',
            name='user_id',
            field=models.BigIntegerField(verbose_name='User id that should be ignored in messages'),
        ),
    ]
