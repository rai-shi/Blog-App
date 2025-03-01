from django.urls import path
from .views import * 

urlpatterns = [

    path('users/', SearchUserView.as_view(), name='search-users'),
    path('blogs/', SearchBlogView.as_view(), name='search-blogs'),
    
    
    
    
    # path('categories/', SearchCategoryView.as_view(), name='search-categories'),
    # path('title/', BlogView.as_view(), name='search-users'),
    # path('category/', BlogView.as_view(), name='search-users'),
    # path('fulltextsearch/', BlogView.as_view(), name='search-users'),
]   
