from django.db import models
from django.contrib.auth.models import User
from Blogs.models import Category

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, related_name="profiles")
    # image = models.ImageField(upload_to="profile_pics", default="default.jpg")

    def __str__(self):
        return self.user.username