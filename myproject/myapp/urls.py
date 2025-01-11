from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload'),
    path('analyze/', views.analyze_data, name='analyze'),
]