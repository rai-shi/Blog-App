from django.shortcuts import render

# rest framework dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.permissions import IsAuthenticated

# swagger documentation libs
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# other requirements
from .serializers import *
from .models import Blog, Category, Comment, Like

# admin page
class CategoryView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():  # Eğer geçerli ise kaydet
            serializer.save()
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED)
        return Response(  # Eğer geçerli değilse hata döndür
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST)




# get all blogs
class BlogView(APIView):
    def get(self, request):
        blogs = Blog.objects.all()
        serializer = BlogsSerializer(blogs, many=True)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK)
                
# get blog detail
class BlogDetailView(APIView):
    def get(self, request, slug):
        blog = Blog.objects.filter(slug=slug).first()
        if not blog:
            raise NotFound("Blog not found")
        serializer = BlogDetailSerializer(blog)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK)


# get all blogs by user
class UserBlogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        blogs = Blog.objects.filter(author=request.user)
        serializer = BlogsSerializer(blogs, many=True)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK)

# get blog detail by user
class UserBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        blog = Blog.objects.filter(author=request.user, slug=slug).first()
        if not blog:
            raise NotFound("Blog not found")
        serializer = BlogDetailSerializer(blog)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK)

    def put(self, request, slug):
        pass

    def delete(self, request, slug):
        blog = Blog.objects.filter(author=request.user, slug=slug).first()
        if not blog:
            raise NotFound("Blog not found")
        blog.delete()
        return Response(
            {"message": "Blog deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT)

# create blog
class CreateBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data 
        data["author"] = request.user.id
        serializer = BlogDetailSerializer(data=data)
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST)
    


