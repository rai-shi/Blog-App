from django.urls import path
from .views import * 
from Blogs.views import UserBlogsView, CreateBlogView, UserBlogView, CommentView

urlpatterns = [
    # POST register
    path('register/', RegisterView.as_view(), name='register'),
    # POST login
    path('login/', LoginView.as_view(), name='login'),
    # GET logout
    path('logout/', LogoutView.as_view(), name='logout'),

    # GET, DELETE user profile
    path('me/', ProfileView.as_view(), name='profile'),

    # GET all
    path('my-blogs/', UserBlogsView.as_view(), name='my-blogs'),

    # POST create blog
    path('my-blogs/new-story/', CreateBlogView.as_view(), name='create-blog'),
    
    # GET blog detail
    path('my-blogs/<slug:slug>/', UserBlogView.as_view(), name='blog-detail'),

    # update user profile, password
]   
