from PyQt5.QtCore import QThread, pyqtSignal
from . import remote, salary, skills
from .styles import CustomWorkbook, CustomWorksheet
from os import path, mkdir


class FileWorker(QThread):
    progressStatus = pyqtSignal(int)
    progressText = pyqtSignal(str)
    taskFinished = pyqtSignal()

    def __init__(self, request, region, pages, areas_dict, object_parser):
        super().__init__()
        self.my_request = request
        self.my_region = region
        self.pages_number = pages
        self._areas_dict = areas_dict
        self._parser = object_parser

    @staticmethod
    def get_path():
        directory = r'../Мои запросы/'
        if not path.exists(directory):
            mkdir(directory)
        return directory

    def run(self):
        my_area_id = self._parser.get_my_area_id(self.my_region, self._areas_dict)

        # Создание файла Excel
        path = self.get_path()
        wb_1 = CustomWorkbook(path, self.my_request, self.my_region)

        # Создание листов
        ws_1 = CustomWorksheet('Вакансии', wb_1)
        ws_2 = CustomWorksheet('Навыки_табл', wb_1)
        ws_3 = CustomWorksheet('Зарплата_табл', wb_1)
        ws_4 = CustomWorksheet('Удалёнка_табл', wb_1)

        # Таблицы 2,3,4 - вспомогательные и должны быть скрыты
        ws_2.hide()
        ws_3.hide()
        ws_4.hide()

        # Форматирование результирующей таблицы
        headlines = ['Должность', 'ЗП (на руки) от, ₽', 'ЗП (на руки) до, ₽', 'Минимум опыта\nлет ',
                     'Удалёнка', 'Опубликовано\n(дней)', 'Создано\n(дней)', 'Компания', 'Подробнее']
        headlines_format, string_format, numbers_format, days_format = wb_1.add_cells_formatting()
        ws_1.add_headlines(headlines, headlines_format)
        ws_1.set_cell_formats(string_format, numbers_format, days_format)
        ws_1.add_conditional_formatting()
        ws_1.freeze_panes(1, 0)
        ws_1.cut_unused_cells(col=9)

        # Запись данных о вакансиях в таблицу
        self._parser.parse_page(self.my_request, my_area_id, self.pages_number, ws_1, self)

        # Создание диаграммы требуемых навыков
        skills.write_skills(ws_2, self._parser)
        skills.create_bar_chart(wb_1, 'Навыки', self.my_request, self.my_region)

        # Создание диаграммы уровня заработной платы
        salary.write_salary_statistics(ws_3, self._parser)
        salary.create_column_chart(wb_1, 'Зарплата', self.my_request, self.my_region)

        # Создание диаграммы формата работы
        remote.write_remote_data(ws_4)
        remote.create_pie_chart(wb_1, 'Удалёнка', self.my_request, self.my_region)

        # Закрытие файла
        wb_1.close()
        print(f'Файл {self.my_request} закрыт.')
        self.taskFinished.emit()
