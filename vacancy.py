from datetime import datetime, date
from re import search


rates = {'RUR': 1, 'USD': 81, 'EUR': 89}


class Vacancy:
    max_row = 2  # Новая строка при записи каждого объекта в Excel файл

    def __init__(self, job):
        self.row = Vacancy.max_row
        Vacancy.max_row += 1

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
        worksheet.write_row(f'A{self.row}', list(self.__dict__.values())[1:-1])
