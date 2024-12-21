from django.contrib import admin
from .models import Profession, SalaryByCity, VacanciesByCity, VacancyOverride

# Register the Profession model to make it manageable via the admin site
@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary_from', 'salary_to', 'city', 'date_posted')  # Fields to display in the list view
    search_fields = ('title', 'city')  # Add search functionality
    list_filter = ('city', 'date_posted')  # Add filters

@admin.register(SalaryByCity)
class SalaryByCityAdmin(admin.ModelAdmin):
    list_display = ('profession', 'city', 'avg_salary')
    list_filter = ('city', 'profession')
    search_fields = ('city',)

# Register the VacanciesByCity model
@admin.register(VacanciesByCity)
class VacanciesByCityAdmin(admin.ModelAdmin):
    list_display = ('profession', 'city', 'count', 'share')
    list_filter = ('city', 'profession')
    search_fields = ('city',)



@admin.register(VacancyOverride)
class VacancyOverrideAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'region', 'date_published')
    search_fields = ('name', 'company_name', 'region')
    list_filter = ('region', 'date_published')