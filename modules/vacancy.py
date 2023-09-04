# /* coding: UTF-8 */

from datetime import datetime, date
from re import search
from .api import rates, russian_areas


class Vacancy:
    max_row = 2  # Новая строка при записи данных каждого объекта в файл

    def __init__(self, job: dict):
        """
        Класс Vacancy представляет собой объект для хранения данных о вакансии.

        :param job: Информация о вакансии в формате JSON.
        """

        self.row = Vacancy.max_row
        Vacancy.max_row += 1

        self.area_id = job['area']['id']

        self.name = job['name']

        self.salary_from, self.salary_to = self.__get_salary_range(job['salary'])

        exp = search(r'\d', job['experience']['name'])
        self.years_of_experience = int(exp.group()) if exp else 0

        self.is_remote = int(job['schedule']['name'] == 'Удаленная работа')

        self.days_since_published = self.__find_timedelta(job['published_at'])
        self.days_since_created = self.__find_timedelta(job['initial_created_at'])

        self.employer_name = job['employer']['name']

        self.url = job['alternate_url']

        self.skills = [skill for dct in job['key_skills'] for skill in dct.values()]

    def __get_salary_range(self, salary: dict) -> tuple:
        """
        Внутренний метод для расчета диапазона заработной платы (чистыми на руки).

        :param salary: Информация о зарплате вакансии в формате JSON.
        :return: Кортеж с нижней и верхней границами заработной платы (чистыми на руки).
        """

        if not salary:
            return '', ''

        k = 1               # Расчёт чистой ЗП проводится только для РФ по НДФЛ 13%.
        if salary['gross'] and self.area_id in russian_areas:
            k = 0.87

        bottom, top, currency = salary['from'], salary['to'], salary['currency']

        def calculate_salary(bound: int | None) -> int:
            """Рассчитывает значение границы (нижней или верхней) с учётом курса валюты и ставки налога."""

            return int(k * bound * (1 / rates[currency])) if bound else ''
        return calculate_salary(bottom), calculate_salary(top)

    @classmethod
    def __find_timedelta(cls, date_obj: str) -> int:
        """
        Внутренний метод для нахождения разницы в днях между текущей датой и указанной датой.

        :param date_obj: Дата в формате строки ('2023-07-27T10:53:02+0300').
        :return: Количество дней между текущей датой и указанной датой.
        """

        published = datetime.strptime(date_obj, '%Y-%m-%dT%H:%M:%S%z')
        return (date.today() - published.date()).days
