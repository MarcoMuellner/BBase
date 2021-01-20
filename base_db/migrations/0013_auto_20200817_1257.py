# Generated by Django 2.2.3 on 2020-08-17 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_db', '0012_auto_20200817_0301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseguild',
            name='mod_role',
            field=models.CharField(default=None, max_length=1024, null=True, verbose_name='Role id of mods'),
        ),
        migrations.AlterField(
            model_name='baseguild',
            name='name',
            field=models.CharField(max_length=1024, verbose_name='Name of server'),
        ),
        migrations.AlterField(
            model_name='baseguild',
            name='prefix',
            field=models.CharField(default=';', max_length=1024, verbose_name='Prefix for guild'),
        ),
        migrations.AlterField(
            model_name='error',
            name='cmd_string',
            field=models.CharField(max_length=10000, verbose_name='Command string that was executed'),
        ),
        migrations.AlterField(
            model_name='error',
            name='error_type',
            field=models.CharField(max_length=10000, verbose_name='Error type'),
        ),
        migrations.AlterField(
            model_name='milestonedata',
            name='name',
            field=models.CharField(max_length=2000, verbose_name='Name of the milestone'),
        ),
    ]
