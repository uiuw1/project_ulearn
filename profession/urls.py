from django.urls import path
from . import views

urlpatterns = [
    path('', views.profession_list, name='profession_list'),
    path('profession/<int:profession_id>/', views.profession_detail, name='profession_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profession/<int:profession_id>/deed-to-deed/', views.deed_to_deed, name='deed_to_deed'),
    path('profession/<int:profession_id>/skills/', views.skills_view, name='skills_view'),


]
