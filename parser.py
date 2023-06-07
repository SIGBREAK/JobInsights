import time
import requests

from datetime import datetime, date
from itertools import count
from re import search
from statistics import mean


rates = {'RUR': 1, 'USD': 81, 'EUR': 89}


class Vacancy:
    max_row = count(2)  # Новая строка при записи каждого объекта в Excel файл

    def __init__(self, job):
        # Название вакансии
        self.name = job['name']

        # Расчёт диапазона заработной платы (чистыми на руки)
        self.salary_from, self.salary_to = self.__get_salary_range(job['salary'])

        # Нахождение требуемого опыта работы
        exp = search('\d', job['experience']['name'])
        self.years_of_experience = int(exp.group()) if exp else 0

        # Проверка на удалённый тип занятости
        self.is_remote = int(job['schedule']['name'] == 'Удаленная работа')

        # Сколько дней назад была опубликована/создана вакансия
        self.days_since_published = self.__find_timedelta(job['published_at'])
        self.days_since_created = self.__find_timedelta(job['initial_created_at'])

        # Название организации
        self.employer_name = job['employer']['name']

        # Ссылка на вакансию
        self.url = job['alternate_url']

        # Сбор данных о требуемых ключевых навыках
        self.skills = [skill for dct in job['key_skills'] for skill in dct.values()]

    @classmethod
    def __get_salary_range(cls, salary):
        if not salary:
            return '', ''

        k = 1
        if salary['gross']:
            k = 0.87

        bottom, top, currency = salary['from'], salary['to'], salary['currency']

        def calculate_salary(bound):
            return int(k * bound * rates[currency]) if bound else ''
        return calculate_salary(bottom), calculate_salary(top)

    @classmethod
    def __find_timedelta(cls, date_obj):
        published = datetime.strptime(date_obj, '%Y-%m-%dT%H:%M:%S%z')
        return (date.today() - published.date()).days

    def write_all_data(self, worksheet):
        row = next(Vacancy.max_row)
        worksheet.write(f'A{row}', self.name)
        worksheet.write_row(f'B{row}', [self.salary_from, self.salary_to, self.years_of_experience, self.is_remote])
        worksheet.write_row(f'F{row}', [self.days_since_published, self.days_since_created])
        worksheet.write_row(f'H{row}', [self.employer_name, self.url])

    def collect_salary_data(self):
        if self.salary_from or self.salary_to:
            salary_tuple = tuple(filter(None, [self.salary_from, self.salary_to]))
            salaries_list.append(mean(salary_tuple))


skills_list = []
salaries_list = []


def get_page(my_request, page=0):
    params = {'text': f'{my_request}',
              'area': 1,
              'page': page,
              'per_page': 100}
    with requests.get('https://api.hh.ru/vacancies', params) as r:
        return r.json()


def parse_page(request, pages, sheet):
    for p in range(pages):
        json_obj = get_page(request, p)
        print(f"По запросу '{request}' всего найдено {json_obj['found']} вакансий.")
        if not json_obj['items']:
            break

        for v, item in enumerate(json_obj['items'], 1):
            if v > 20:
                break
            with requests.get(item['url']) as request:
                vacancy = Vacancy(request.json())
                vacancy.write_all_data(sheet)
                vacancy.collect_salary_data()
                skills_list.extend(vacancy.skills)

            print(f'Записаны данные: страница {p + 1}, вакансия {v}.')
            time.sleep(0.35)  # обход бана от API hh.ru
        print(f'Пройдена страница: {p + 1}.')
        time.sleep(5)
