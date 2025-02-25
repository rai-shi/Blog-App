from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Blog, Category, Comment, Like



class BlogDetailSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True  
    )
    category_names = serializers.SerializerMethodField()  
    author_name = serializers.SerializerMethodField()


    class Meta:
        model = Blog
        fields = "__all__"
        extra_kwargs = {
            "slug": {"read_only": True},
            "category_names": {"read_only": True},
            "author_name": {"read_only": True},
            "author": {"write_only": True}
        }

    def get_category_names(self, obj):
        return [{"name":category.name, "id":category.id} for category in obj.categories.all()]
    def get_author_name(self, obj):
        return {"name":obj.author.username, "id":obj.author.id}


# for getting all blogs
class BlogsSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    class Meta:
        model = Blog
        fields = ["author", "slug", "title", "description", "categories", "created_at"]

    def get_categories(self, obj):
        return [category.name for category in obj.categories.all()]
    def get_author(self, obj):
        return obj.author.username


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["slug", "name"]
        extra_kwargs = {
            "slug": {"read_only": True}
        }

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"