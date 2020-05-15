# Generated by Django 3.0.5 on 2020-05-14 02:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interceptor', '0003_interceptedrequest_content_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterceptedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter', models.CharField(max_length=250)),
                ('filename', models.CharField(max_length=250)),
                ('size', models.FloatField(blank=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interceptor.InterceptedRequest')),
            ],
        ),
    ]
