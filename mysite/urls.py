"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from profession import views  # Import views from the profession app


urlpatterns = [
    path('admin/', admin.site.urls),
    path('profession/', views.profession_list, name='profession_list'),  # Add this line
    path('general-statistics/', views.general_statistics, name='general_statistics'),
    path('profession/<int:profession_id>/deed-to-deed/', views.deed_to_deed, name='deed_to_deed'),
    path('profession/<int:profession_id>/geography/', views.geography, name='geography'),
    path('profession/<int:profession_id>/skills/', views.skills_view, name='skills_view'),
    path('profession/<int:profession_id>/last-vacancies/', views.last_vacancies, name='last_vacancies'),
]
