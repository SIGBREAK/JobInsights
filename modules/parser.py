# /* coding: UTF-8 */

from time import sleep
from requests import get
from statistics import mean
from itertools import count
from .vacancy import Vacancy
from .api import get_page


class Parser:
    """
    Класс необходимый для постраничного парсинга вакансий, использует API hh.ru.

    Экземпляр класса Parser обладает двумя локальными атрибутами:
        1) список средних значений, взятых из диапазонов ЗП;
        2) список требуемых навыков.
    """

    def __init__(self):
        self.salaries_list = []
        self.skills_list = []
        self.__stop = False

    def stop_parsing(self) -> None:
        """
        Функция останавливает парсинг страницы и привязана к кнопке СТОП интерфейса программы.

        :return: None
        """

        self.__stop = True

    def collect_salary_data(self, vacancy: Vacancy) -> None:
        """
        Функция определяет среднее значение для диапазона заработной платы (если таковой указан в вакансии),
        полученное значение сохраняется в локальный атрибут salaries_list (класса Parser).

        Если для объекта класса Vacancy не указаны данные о ЗП - ничего не происходит.

        :param vacancy: текущая вакансия (экземпляр класса Vacancy).
        :return: None.
        """

        if vacancy.salary_from or vacancy.salary_to:
            salary_tuple = tuple(filter(None, (vacancy.salary_from, vacancy.salary_to)))
            self.salaries_list.append(mean(salary_tuple))

    def collect_skills_data(self, vacancy: Vacancy) -> None:
        """
        Функция добавляет данные о ключевых навыках, указанных в вакансии в атрибут skills_list, который потом будет
        использован для вывода ТОП-20 навыков.

        :param vacancy: текущая вакансия (экземпляр класса Vacancy).
        :return: None.
        """

        self.skills_list.extend(vacancy.skills)

    def get_collected_data(self):
        """Функция возвращает salaries_list и skills_list, соответственно."""

        return self.salaries_list, self.skills_list

    def parse_page(self, request: str, area_id: int, pages: int,
                   period: int,  only_with_salary: bool, order_by: str, sheet, worker) -> None:
        """
        Функция осуществляет парсинг страницы. Каждую итерацию она:
            1) записывает данные в Excel (в главную и вспомогательные таблицы);
            2) подаёт два сигнала на GUI (progressUpdated и progressText);
            3) собирает данные о ЗП и навыках в локальные атрибуты (salaries_list и skills_list).

        Примечание! Поиск не происходит, если на странице не найдено вакансий.

        Ограничение! Для обхода блокировки (Captcha) от API hh.ru вводится задержка обработчика событий.

        :param request: текст запроса пользователя.
        :param area_id: id города (региона) пользователя.
        :param pages: кол-во анализируемых страниц.
        :param period: период, в который были опубликованы вакансии.
        :param order_by: сортировка JSON по (соответствию, дате, убыванию и возрастанию дохода).
        :param only_with_salary: в выборку JSON попадают только вакансии с указанной ЗП.
        :param sheet: лист (объект класса Worksheet), куда будет осуществляться запись.
        :param worker: поток (объект класса FileWorker), который принимает сигналы и посылает их на GUI.
        :return: None.
        """

        counter = count(1)

        for page in range(pages):
            items, found = get_page(request, area_id, period, only_with_salary, order_by, page)
            if not items:
                return

            for item in items:
                if self.__stop:
                    self.__stop = False
                    return

                with get(item['url']) as r:
                    if r.status_code != 200:
                        print(f'Поиск прерван со стороны сервера {r.status_code}. Файл будет закрыт.')
                        return

                    vacancy = Vacancy(r.json())

                    row = next(counter)
                    worker.progressStatus.emit(int(100 * row / min(found, 100 * pages)))
                    worker.progressText.emit(vacancy.name[:70])

                    sheet.write_all_data(vacancy, row=row + 1)
                    self.collect_salary_data(vacancy)
                    self.collect_skills_data(vacancy)

                sleep(0.5)  # Пока что парсер синхронный, поэтому блочим обработчик событий на 0.5 сек каждую итерацию.
            if page not in (found // 100, pages - 1):
                sleep(5)


parser = Parser()
