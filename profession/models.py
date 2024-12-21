from django.db import models

class Profession(models.Model):
    title = models.CharField(max_length=255)
    salary_from = models.DecimalField(max_digits=10, decimal_places=2)
    salary_to = models.DecimalField(max_digits=10, decimal_places=2)
    city = models.CharField(max_length=255)
    key_skills = models.CharField(max_length=255)
    description = models.TextField()
    date_posted = models.DateTimeField()

    def __str__(self):
        return self.title


class SalaryByCity(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='salary_by_city')
    city = models.CharField(max_length=255)
    avg_salary = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-avg_salary']  # Order by descending salary

    def __str__(self):
        return f"{self.city} - {self.profession.title} Salary"


class VacanciesByCity(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='vacancies_by_city')
    city = models.CharField(max_length=255)
    count = models.IntegerField()
    share = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage share of vacancies

    class Meta:
        ordering = ['-share']  # Order by descending share

    def __str__(self):
        return f"{self.city} - {self.profession.title} Vacancies"



from django.db import models

class VacancyOverride(models.Model):
    vacancy_id = models.CharField(max_length=255, unique=True, help_text="Unique ID for the vacancy from the API")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    key_skills = models.TextField(blank=True, null=True, help_text="Comma-separated list of skills")
    company_name = models.CharField(max_length=255)
    salary_from = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_to = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    region = models.CharField(max_length=255)
    date_published = models.DateTimeField()

    def __str__(self):
        return self.name
