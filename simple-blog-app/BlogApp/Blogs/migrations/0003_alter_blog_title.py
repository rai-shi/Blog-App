# Generated by Django 5.1.6 on 2025-02-28 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Blogs", "0002_blog_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blog",
            name="title",
            field=models.CharField(max_length=1000),
        ),
    ]
