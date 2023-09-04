# /* coding: UTF-8 */

from requests import get


def get_rates() -> dict[str, str]:
    """
    Функция для получения курса валют по API hh.ru.

    :return: Словарь с курсами валют {код_валюты: курс}.
    """

    with get('https://api.hh.ru/dictionaries') as r:
        return {curr['code']: curr['rate'] for curr in r.json()['currency']}


def get_vacancy_search_order():
    """Возвращает ключи сортировок получаемых вакансий в JSON'ах. (Кроме ключа связанного с расстоянием)."""

    with get('https://api.hh.ru/dictionaries') as r:
        return {curr['name']: curr['id'] for curr in r.json()['vacancy_search_order'] if curr['id'] != 'distance'}


def get_my_area_id(my_region: str, areas: dict[str, str]) -> int:
    """
    Функция возвращает актуальный id заданного пользователем региона.

        Примечание! Предварительно должен быть сформирован словарь areas c актуальными id для различных регионов.

    :param my_region: город (регион) пользователя.
    :param areas: словарь, полученный от API {id: название}.
    :return: id города (региона).
    """

    for area_id, name_area in areas.items():
        if name_area.lower() == my_region.lower():
            return int(area_id)


def get_page(request: str, area_id: int, period,
             only_with_salary=False, order_by='relevance', page=0) -> tuple:
    """
    Функция необходима для создания запроса к API hh.ru с целью - получения данных о вакансиях.

    :param request: текст запроса пользователя.
    :param area_id: id города (региона) пользователя.
    :param period: период, в который были опубликованы вакансии.
    :param only_with_salary: в выборку JSON попадают только вакансии с указанной ЗП.
    :param order_by: сортировка JSON по (соответствию, дате, убыванию и возрастанию дохода).
    :param page: номер страницы по порядку (начинается от нуля).
    :return:
            1) JSON-объект с вакансиями;
            2) количество найденных вакансий по запросу.
    """

    params = {'text': request,
              'area': area_id,
              'page': page,
              'per_page': 100,
              'only_with_salary': only_with_salary,
              'order_by': order_by,
              'period': period}

    with get('https://api.hh.ru/vacancies', params=params) as r:
        json_object = r.json()
        return json_object['items'], json_object['found']


def init_areas():
    """
    Функция собирает актуальные данные о городах и регионах {id: название},
    что позволяет не привязываться к id, которые могут быть изменены в API hh.ru.

    :return:
            Словарь городов (регионов) {id: название},
            Множество id городов и областей, относящихся только к РФ (для расчёта чистой ЗП).
    """

    with get('https://api.hh.ru/areas') as r:
        json_obj = r.json()

    def get_areas(locations, in_russia=False):
        areas = {}

        if in_russia:
            locations = filter(lambda item: item['name'] == 'Россия', locations)

        for loc in locations:
            areas[loc['id']] = loc['name']
            if loc['areas']:
                areas.update(get_areas(loc['areas']))

        return areas

    all_locations = get_areas(json_obj)
    russian_areas = set(get_areas(json_obj, in_russia=True))

    return all_locations, russian_areas


rates = get_rates()
areas, russian_areas = init_areas()
vacancy_search_order = get_vacancy_search_order()
