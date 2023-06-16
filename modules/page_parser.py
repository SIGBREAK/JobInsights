from time import sleep
from requests import get
from statistics import mean
from itertools import count
from .vacancy import Vacancy
from typing import Dict


class Parser:
    """
    Класс необходимый для постраничного парсинга вакансий, использует API hh.ru.

    Экземпляр класса Parser обладает двумя локальными атрибутами:
        1) список средних значений, взятых из диапазонов ЗП;
        2) список требуемых навыков.
    """

    def __init__(self):
        self._stop = False
        self.salaries_list = []
        self.skills_list = []

    @staticmethod
    def init_areas_dict() -> Dict[str, str]:
        """
        Функция собирает актуальные данные о городах и регионах {id: название},
        что позволяет не привязываться к айдишникам, которые могут быть изменены в API hh.ru.

            Примечание! Функция должна быть вызвана при формировании главного окна.

            Ограничение! Сбор данных осуществляется только по территории РФ.

        :return: словарь городов (регионов) {id: название}.
        """

        with get('https://api.hh.ru/areas') as r:
            json_obj = r.json()

        areas = {}
        for country in filter(lambda item: item['name'] == 'Россия', json_obj):
            areas[country['id']] = country['name']
            for region in country['areas']:
                areas[region['id']] = region['name']
                for area in region['areas']:
                    areas[area['id']] = area['name']
        return areas

    @staticmethod
    def get_my_area_id(my_region: str, areas: Dict[str, str]) -> int:
        """
        Функция возвращает актуальный id заданного пользователем региона.

            Примечание! Предварительно должен быть сформирован словарь areas c актуальными id для различных регионов.

        :param my_region: город (регион) пользователя
        :param areas: словарь, полученный от API {id: название}
        :return: id города (региона)
        """

        for area_id, name_area in areas.items():
            if name_area.lower() == my_region.lower():
                return int(area_id)

    def collect_salary_data(self, vacancy: Vacancy) -> None:
        """
        Функция определяет среднее значение для диапазона заработной платы (если таковой указан в вакансии),
        полученное значение сохраняется в локальный атрибут salaries_list (класса Parser).

        Если для объекта класса Vacancy не указаны данные о ЗП - ничего не происходит.

        :param vacancy: текущая вакансия (экземпляр класса Vacancy)
        :return: None
        """

        if vacancy.salary_from or vacancy.salary_to:
            salary_tuple = tuple(filter(None, (vacancy.salary_from, vacancy.salary_to)))
            self.salaries_list.append(mean(salary_tuple))

    @staticmethod
    def get_page(my_request: str, my_area_id: int, page=0):
        """
        Функция необходима для создания запроса к API hh.ru. с целью - получения данных о вакансиях.

        :param my_request: текст запроса пользователя
        :param my_area_id: id города (региона) пользователя
        :param page: номер страницы по порядку (начинается от нуля)
        :return:
                1) JSON-объект с вакансиями;
                2) количество найденных вакансий по запросу.
        """

        params = {'text': f'{my_request}',
                  'area': my_area_id,
                  'page': page,
                  'per_page': 100}
        with get('https://api.hh.ru/vacancies', params) as r:
            json_object = r.json()
            return json_object['items'], json_object['found']

    def stop_parsing(self) -> None:
        """
        Функция останавливает парсинг страницы и привязана к кнопке СТОП интерфеса программы.

        :return: None
        """

        self._stop = True

    def parse_page(self, my_request: str, my_area_id: int, pages_number: int, sheet, worker) -> None:
        """
        Функция осуществляет парсинг страницы. В ходе работы:
            1) записывает данные в Excel (в главную и вспомогательные таблицы);
            2) подаёт два сигнала на GUI (progressUpdated и progressText);
            3) собриает данные о ЗП и навыках в в локальные атрибуты (salaries_list и skills_list).

        Примечание! Поиск не происходит, если на странице не найдено вакансий.

        Ограничение! Для обхода блокировки (требования ввести капчу) от API hh.ru вводится задержка обработчика событий.

        :param my_request: текст запроса пользователя
        :param my_area_id: id города (региона) пользователя
        :param pages_number: кол-во анализируемых страниц
        :param sheet: лист (объект класса Worksheet), куда будет осуществляться запись
        :param worker: поток (объект класса FileWorker), который принимает сигналы и посылать их на GUI
        :return: None
        """

        counter = count(1)

        for page in range(pages_number):
            items, found = self.get_page(my_request, my_area_id, page)
            if not items:
                break

            for item in items:
                if self._stop:
                    self._stop = False
                    return

                with get(item['url']) as r:
                    vacancy = Vacancy(r.json())

                    worker.progressStatus.emit(int(100 * next(counter) / min(found, 100 * pages_number)))
                    worker.progressText.emit(vacancy.name[:70])

                    vacancy.write_all_data(sheet)
                    self.collect_salary_data(vacancy)
                    self.skills_list.extend(vacancy.skills)

                sleep(0.35)
            if page not in (found // 100, pages_number - 1):
                sleep(5)
