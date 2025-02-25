from django.urls import path
from .views import * 

urlpatterns = [

    path('', BlogView.as_view(), name='all-blogs'),
    path('category/', CategoryView.as_view(), name='category'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='blog-detail'),
]   
