# Generated by Django 5.1.6 on 2025-02-28 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Blogs", "0004_alter_blog_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blog",
            name="slug",
            field=models.SlugField(blank=True, max_length=500, unique=True),
        ),
    ]
