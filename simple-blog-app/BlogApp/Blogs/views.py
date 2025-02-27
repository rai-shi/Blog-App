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
        serializer_data = serializer.data

        for i, blog in enumerate(blogs):
            serializer_data[i]["comment_count"] = blogCommentCount(blog)
            serializer_data[i]["like_count"] = getLikeCount(blog)

        return Response(
            serializer_data,
            status=status.HTTP_200_OK)
                
# get blog detail
class BlogDetailView(APIView):
    def get(self, request, slug):
        blog = Blog.objects.filter(slug=slug).first()

        if not blog:
            raise NotFound("Blog not found")
        
        serializer = BlogDetailSerializer(blog)
        serializer_data = serializer.data

        comments, comment_count = getBlogComment(blog)
        serializer_data["comments"] = comments
        serializer_data["comment_count"] = comment_count
        serializer_data["like_count"] = getLikeCount(blog)

        return Response(
            serializer_data, 
            status=status.HTTP_200_OK)



# get all blogs by user
class UserBlogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        blogs = Blog.objects.filter(author=request.user)
        serializer = BlogsSerializer(blogs, many=True)
        serializer_data = serializer.data

        for i, blog in enumerate(blogs):
            serializer_data[i]["comment_count"] = blogCommentCount(blog)
            serializer_data[i]["like_count"] = getLikeCount(blog)

        return Response(
            serializer_data,
            status=status.HTTP_200_OK)

# get blog detail by user
class UserBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        blog = Blog.objects.filter(author=request.user, slug=slug).first()
        
        if not blog:
            raise NotFound("Blog not found")
        
        serializer = BlogDetailSerializer(blog)
        serializer_data = serializer.data

        comments, comment_count = getBlogComment(blog)
        serializer_data["comments"] = comments
        serializer_data["comment_count"] = comment_count
        serializer_data["like_count"] = getLikeCount(blog)

        return Response(
            serializer_data, 
            status=status.HTTP_200_OK)

    def put(self, request, slug):
        blog = Blog.objects.filter(author=request.user, slug=slug).first()
        
        if not blog:
            raise NotFound("Blog not found")
        
        data = request.data
        serializer = BlogUpdateSerializer(blog, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, 
                status=status.HTTP_200_OK)
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST)

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
    


def getBlogComment(blog):
    serializer = CommentSerializer(blog.comments, many=True)
    return serializer.data, len(serializer.data)

def blogCommentCount(blog):
    return blog.comments.count()

class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        blog = Blog.objects.filter(slug=slug).first()
        if not blog:
            raise NotFound("Blog not found")
        comments = Comment.objects.filter(post=blog)
        serializer = CommentSerializer(comments, many=True)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK)

    def post(self, request, slug):
        
        comment = request.data['comment']
        blog = Blog.objects.filter(slug=slug).first()
        if not blog:
            raise NotFound("Blog not found")
        comment = Comment.objects.create(
            post=blog,
            user=request.user,
            content=comment
        )
        serializer = CommentSerializer(comment)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED)

class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, id):
        comments = Comment.objects.get(id=id)
        if not comments:
            raise NotFound("Comment not found")
        serializer = CommentSerializer(comments)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK)

    
    def delete(self, request, slug, id): 
        comment = Comment.objects.get(id=id)
        if not comment:
            raise NotFound("Comment not found")
        comment.delete()
        return Response(
            {"message": "Comment deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT)


def getLikeCount(blog):
    return blog.likes.count()

class LikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, slug):
        blog = Blog.objects.filter(slug=slug).first()
        if not blog:
            raise NotFound("Blog not found")
        
        like, created = Like.objects.get_or_create(user=request.user, post=blog)
        
        if not created:
            return Response({"message": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Liked successfully"}, status=status.HTTP_201_CREATED)
    
    
    def delete(self, request, slug):
        blog = Blog.objects.filter(slug=slug).first()
        if not blog:
            raise NotFound("Blog not found")
        
        like = Like.objects.filter(user=request.user, post=blog).first()
        
        if not like:
            raise NotFound("Like not found")
        
        like.delete()
        return Response(
            {"message": "Like removed successfully"}, 
            status=status.HTTP_204_NO_CONTENT)