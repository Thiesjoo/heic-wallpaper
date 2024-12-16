# Generated by Django 5.1.4 on 2024-12-10 23:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallpaper',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uid', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[(1, 'Ready'), (2, 'Uploading'), (3, 'Processing'), (4, 'Error'), (5, 'Deleted')], max_length=255)),
                ('type', models.CharField(choices=[(1, 'Generic'), (2, 'Time Based')], max_length=255)),
                ('data', models.JSONField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]