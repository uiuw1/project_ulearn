import datetime
from datetime import datetime, timedelta
import requests
from django.db.models import Count, Avg, F
from django.shortcuts import render, get_object_or_404
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import JsonResponse
import base64
import random
from .models import Profession, SalaryByCity, VacanciesByCity, VacancyOverride
from collections import Counter

# Function to get currency conversion rates
def get_currency_rate(from_currency, to_currency="RUB"):
    # You can replace this with another currency conversion API
    url = f"https://v6.exchangerate-api.com/v6/YOUR_API_KEY/latest/{from_currency}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "conversion_rates" in data:
            return data["conversion_rates"].get(to_currency, 1)  # Default to 1 if conversion rate not found
    return 1  # Return 1 if the API call fails or if the currency conversion rate is not found

def profession_detail(request, profession_id):
    profession = get_object_or_404(Profession, id=profession_id)
    return render(request, 'profession/profession_detail.html', {'profession': profession})

def about(request):
    return render(request, 'profession/about.html')

def contact(request):
    return render(request, 'profession/contact.html')

def profession_list(request):
    professions = Profession.objects.all()
    return render(request, 'profession/profession_list.html', {'professions': professions})

def general_statistics(request):
    professions = Profession.objects.all()

    # Exclude incorrectly filled salaries
    valid_professions = professions.filter(salary_to__lte=10_000_000)

    # 1. Dynamics of the level of wages by year
    salary_by_year = {}
    for profession in valid_professions:
        year = profession.date_posted.year
        avg_salary = (profession.salary_from + profession.salary_to) / 2

        # Convert salary to RUB if the currency is not already RUB
        if profession.city and profession.salary_from and profession.salary_to:
            # Assuming the salary is provided in a currency other than RUB, for example, USD
            if profession.city == "SomeCity":  # Replace with your actual logic to detect the currency
                currency_rate = get_currency_rate("USD")  # Use your own logic for the correct currency
                avg_salary = avg_salary * currency_rate

        salary_by_year.setdefault(year, []).append(avg_salary)

    salary_dynamics = {year: sum(salaries) / len(salaries) for year, salaries in salary_by_year.items()}

    # 2. Dynamics of the number of vacancies by year
    vacancies_by_year = (
        valid_professions
        .annotate(year=F('date_posted__year'))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )

    # 3. Level of salaries by cities
    salary_by_city = (
        valid_professions
        .values('city')
        .annotate(avg_salary=Avg((F('salary_from') + F('salary_to')) / 2))
        .order_by('-avg_salary')
    )

    # 4. Share of vacancies in cities
    total_vacancies = valid_professions.count()
    city_shares = (
        valid_professions
        .values('city')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    city_shares = [
        {'city': data['city'], 'share': round((data['count'] / total_vacancies) * 100, 2)}
        for data in city_shares
    ]

    # 5. Top 20 skills by year
    key_skills = valid_professions.values_list('key_skills', flat=True)
    skills_counter = Counter(skill.strip() for skills in key_skills for skill in skills.split(','))
    top_skills = skills_counter.most_common(20)

    context = {
        'salary_dynamics': salary_dynamics,
        'vacancies_by_year': vacancies_by_year,
        'salary_by_city': salary_by_city,
        'city_shares': city_shares,
        'top_skills': top_skills,
    }

    return render(request, 'profession/general_statistics.html', context)

# The new view for "The Deed to Deed"
def deed_to_deed(request, profession_id):
    profession = get_object_or_404(Profession, id=profession_id)

    # Filter professions by the selected profession
    selected_profession = Profession.objects.filter(id=profession_id)

    # 1. Dynamics of wages by years for the chosen profession
    salary_by_year = {}
    for profession in selected_profession:
        year = profession.date_posted.year
        avg_salary = (profession.salary_from + profession.salary_to) / 2

        # Convert salary to RUB if the currency is not already RUB
        if profession.city and profession.salary_from and profession.salary_to:
            if profession.city == "SomeCity":  # Replace with your actual logic to detect the currency
                currency_rate = get_currency_rate("USD")  # Replace with correct currency logic
                avg_salary = avg_salary * currency_rate

        salary_by_year.setdefault(year, []).append(avg_salary)

    salary_dynamics = {year: sum(salaries) / len(salaries) for year, salaries in salary_by_year.items()}

    # 2. Dynamics of the number of vacancies by year for the chosen profession
    vacancies_by_year = (
        selected_profession
        .annotate(year=F('date_posted__year'))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )

    context = {
        'profession': profession,
        'salary_dynamics': salary_dynamics,
        'vacancies_by_year': vacancies_by_year,
    }

    #fwaf

    return render(request, 'profession/deed_to_deed.html', context)



def geography(request, profession_id):
    # Get the profession
    profession = Profession.objects.get(id=profession_id)

    # Fetch the salary and vacancies data
    salary_by_city = SalaryByCity.objects.filter(profession=profession).order_by('-avg_salary')
    vacancies_by_city = VacanciesByCity.objects.filter(profession=profession).order_by('-share')

    # Pass data to the template
    context = {
        'profession': profession,
        'salary_by_city': salary_by_city,
        'vacancies_by_city': vacancies_by_city,
    }

    return render(request, 'profession/geography.html', context)


#SEE TOP SKILLS


def skills_view(request, profession_id):
    # Get the profession by ID
    profession = Profession.objects.get(id=profession_id)

    # Split the skills by comma and count occurrences
    all_skills = []
    for profession in Profession.objects.all():
        skills = profession.key_skills.split(',')
        all_skills.extend(skills)

    # Count the frequency of each skill
    skill_counts = Counter(all_skills)

    # Get the top 20 skills
    top_20_skills = skill_counts.most_common(20)

    # Prepare data for the chart
    skills = [skill for skill, _ in top_20_skills]
    counts = [count for _, count in top_20_skills]

    # Create a plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(skills, counts, color='skyblue')
    ax.set_xlabel('Frequency')
    ax.set_title('Top 20 Skills by Year')

    # Convert the plot to a PNG image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'profession/skills.html', {
        'profession': profession,
        'top_20_skills': top_20_skills,
        'image_base64': image_base64
    })



#LAST PAGE

def last_vacancies(request, profession_id):
    # Define the API endpoint
    url = f'https://api.hh.ru/vacancies?specialization={profession_id}&date_from={(datetime.now() - timedelta(days=1)).isoformat()}'

    # Make the GET request to fetch the last 24 hours of vacancies
    response = requests.get(url)
    if response.status_code == 200:
        vacancies_data = response.json()
        # Extract relevant data (assuming 'items' contains the list of vacancies)
        api_vacancies = vacancies_data.get('items', [])
    else:
        api_vacancies = []

    # Process vacancies to include overrides from the database
    vacancies = []
    for vacancy in api_vacancies:
        vacancy_id = vacancy.get('id')
        override = VacancyOverride.objects.filter(vacancy_id=vacancy_id).first()

        if override:
            # Use data from the override
            vacancies.append({
                'name': override.name,
                'description': override.description or vacancy.get('description', "No description available"),
                'key_skills': override.key_skills.split(',') if override.key_skills else [],
                'company': {'name': override.company_name},
                'salary': {'from': override.salary_from, 'to': override.salary_to},
                'region': {'name': override.region},
                'date_published': override.date_published,
            })
        else:
            # Use API data if no override exists
            vacancies.append({
                'name': vacancy.get('name', "Unknown"),
                'description': vacancy.get('description', "No description available"),
                'key_skills': vacancy.get('key_skills', []),
                'company': {'name': vacancy.get('employer', {}).get('name', "Unknown")},
                'salary': vacancy.get('salary', {}),
                'region': {'name': vacancy.get('area', {}).get('name', "Unknown")},
                'date_published': vacancy.get('published_at'),
            })

    # Prepare the context for the template
    context = {
        'vacancies': vacancies,
        'profession_id': profession_id,
    }

    return render(request, 'profession/last_vacancies.html', context)