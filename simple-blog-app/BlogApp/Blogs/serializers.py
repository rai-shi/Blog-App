from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Blog, Category, Comment, Like



class BlogDetailSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)

    class Meta:
        model = Blog
        fields = "__all__"
        extra_kwargs = {
            "slug": {"read_only": True}
        }

    def get_categories(self, obj):
        my_list = [category.name for category in obj.categories.all()]
        print(my_list)
        return my_list
    
    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])
        blog = Blog.objects.create(**validated_data)
        blog.categories.set(categories_data)  
        return blog

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', [])
        instance = super().update(instance, validated_data)
        instance.categories.set(categories_data)  
        return instance

# for getting all blogs
class BlogsSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    class Meta:
        model = Blog
        fields = ["slug", "title", "description", "categories", "created_at"]

    def get_categories(self, obj):
        return [category.name for category in obj.categories.all()]


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