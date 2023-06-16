import time
import requests

from vacancy import Vacancy
from statistics import mean
from itertools import count


class Parser:
    def __init__(self):
        self.stop_search = False
        self.skills_list = []
        self.salaries_list = []

    @staticmethod
    def init_areas_dict():
        """
        Функция вызывается в момент запуска программы и собирает данные о городах (id: название города),
        что позволяет не привязываться к айдишникам, которые могут быть изменены в API hh.ru.
        """

        with requests.get('https://api.hh.ru/areas') as r:
            json_obj = r.json()

        areas = {}
        for country in filter(lambda item: item['name'] == 'Россия', json_obj):
            areas[country['id']] = country['name']
            for region in country['areas']:
                areas[region['id']] = region['name']
                for area in region['areas']:
                    areas[area['id']] = area['name']

        return dict(sorted(areas.items(), key=lambda tpl: int(tpl[0])))

    @staticmethod
    def get_my_area_id(my_region, areas):
        """
        Функция позволяет получить текущий (согласно API hh.ru) айдишник заданного региона.
        Предварительно должен быть сформирован словарь актуальными айдишниками для регионов.
        """
        for area_id, name_area in areas.items():
            if name_area.lower() == my_region.lower():
                return int(area_id)

    def collect_salary_data(self, vacancy):
        if vacancy.salary_from or vacancy.salary_to:
            salary_tuple = tuple(filter(None, [vacancy.salary_from, vacancy.salary_to]))
            self.salaries_list.append(mean(salary_tuple))

    @staticmethod
    def get_page(my_request, my_area_id, page=0):
        params = {'text': f'{my_request}',
                  'area': my_area_id,
                  'page': page,
                  'per_page': 100}
        with requests.get('https://api.hh.ru/vacancies', params) as r:
            return r.json()

    def stop_searching(self):
        self.stop_search = True

    def parse_page(self, my_request, my_area_id, pages, sheet, worker_object):
        total = min(self.get_page(my_request, my_area_id)['found'], pages * 100)
        counter = count(1)

        for p in range(pages):
            json_obj = self.get_page(my_request, my_area_id, p)
            print('Поиск по запросу:', my_request)
            if not json_obj['items']:
                break

            for n, item in enumerate(json_obj['items'], 1):
                # if n > 10:
                #     break

                if self.stop_search:
                    print('Поиск завершён по требованию пользователя.')
                    self.stop_search = False
                    return

                worker_object.progressUpdated.emit(int(100 * next(counter) / total))

                with requests.get(item['url']) as req:
                    vacancy = Vacancy(req.json())

                    worker_object.progressText.emit(vacancy.name[:70])

                    vacancy.write_all_data(sheet)
                    self.collect_salary_data(vacancy)
                    self.skills_list.extend(vacancy.skills)

                print(f'Записаны данные: страница {p + 1}, вакансия {n}.')
                time.sleep(0.35)  # обход бана от API hh.ru
            print(f'Пройдена страница: {p + 1}.')
            time.sleep(5)
