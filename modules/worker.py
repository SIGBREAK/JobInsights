from os import path, mkdir
from PyQt5.QtCore import QThread, pyqtSignal
from .excel import CustomWorkbook, CustomWorksheet
from .parser import Parser


class FileWorker(QThread):
    progressStatus = pyqtSignal(int)
    progressText = pyqtSignal(str)
    taskFinished = pyqtSignal()

    def __init__(self, request, region, area_id, pages):
        super().__init__()
        self.my_request = request
        self.my_region = region
        self.area_id = area_id
        self.pages_number = pages

    @staticmethod
    def get_path():
        directory = r'../Мои запросы/'
        if not path.exists(directory):
            mkdir(directory)
        return directory

    def create_workbook(self):
        directory = self.get_path()
        return CustomWorkbook(directory, self.my_request, self.my_region)

    @staticmethod
    def create_sheets(workbook):
        ws_1 = CustomWorksheet('Вакансии', workbook)
        ws_2 = CustomWorksheet('Навыки_табл', workbook)
        ws_3 = CustomWorksheet('Зарплата_табл', workbook)
        ws_4 = CustomWorksheet('Удалёнка_табл', workbook)
        return ws_1, ws_2, ws_3, ws_4

    @staticmethod
    def hide_data_sheets(*sheets):
        for s in sheets:
            s.hide()

    @staticmethod
    def format_main_table(table_sheet, formats_from):
        headlines_format, string_format, numbers_format, days_format = formats_from.make_cells_formats()
        table_sheet.add_headlines(headlines_format)
        table_sheet.set_cell_formats(string_format, numbers_format, days_format)
        table_sheet.add_conditional_formatting()
        table_sheet.freeze_panes(1, 0)
        table_sheet.cut_unused_cells(col=9)

    def write_data(self, area_id, table, *others):
        parser_obj = Parser()
        parser_obj.parse_page(self.my_request, area_id, self.pages_number, table, worker=self)

        salaries, skills = parser_obj.get_collected_data()

        others[0].write_skills(skills)
        others[1].write_salary_statistics(salaries)
        others[2].write_remote_data()

    @staticmethod
    def create_charts(workbook):
        workbook.create_bar_chart('Навыки')
        workbook.create_column_chart('Зарплата')
        workbook.create_pie_chart('Удалёнка')

    def close_workbook(self, workbook):
        workbook.close()
        print(f'Файл {self.my_request} закрыт.')
        self.taskFinished.emit()

    def run(self):
        workbook = self.create_workbook()

        table, skills, salary, remote = self.create_sheets(workbook)

        self.hide_data_sheets(skills, salary, remote)

        self.format_main_table(table, formats_from=workbook)

        self.write_data(self.area_id, table, skills, salary, remote)

        self.create_charts(workbook)

        self.close_workbook(workbook)
