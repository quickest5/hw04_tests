# Generated by Django 2.2.19 on 2022-09-02 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220902_0952'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='slug',
            field=models.SlugField(default='empty'),
        ),
    ]
