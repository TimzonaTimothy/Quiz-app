# Generated by Django 3.0.5 on 2022-05-29 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0006_auto_20220511_1255'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='ref',
        ),
        migrations.AddField(
            model_name='payment',
            name='serial',
            field=models.CharField(default='ETWo5JTebU', max_length=100),
        ),
        migrations.AlterField(
            model_name='payment',
            name='code',
            field=models.CharField(blank=True, default='xEfgPHDA', max_length=8, null=True, unique=True),
        ),
    ]
