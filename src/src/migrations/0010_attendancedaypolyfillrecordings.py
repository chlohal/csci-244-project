# Generated by Django 5.0.1 on 2024-04-26 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0009_flowinstancestate'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceDayPolyfillRecordings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_at', models.DateTimeField()),
                ('section', models.CharField(max_length=10)),
                ('status', models.CharField(max_length=10)),
                ('student_email', models.CharField(max_length=700)),
                ('instructor_access', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='src.canvastoken')),
            ],
        ),
    ]
