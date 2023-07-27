from requests import get
from typing import Dict


def get_rates():
    with get('https://api.hh.ru/dictionaries') as r:
        return {curr['code']: curr['rate'] for curr in r.json()['currency']}


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


def check_for_vacancies(request, area_id):
    _, found = get_page(request, area_id)

    if not request:
        return 0
    return found


rates = get_rates()
areas_dict = init_areas_dict()
