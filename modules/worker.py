from os import path, mkdir
from PyQt5.QtCore import QThread, pyqtSignal
from .excel import CustomWorkbook, CustomWorksheet
from .parser import parser


class FileWorker(QThread):
    """
    Класс FileWorker представляет собой объект для работы с файлами Excel. Класс унаследован от QThread,
    что позволяет выполнять работу в фоновом режиме для избежания блокировки пользовательского интерфейса.

    Класс FileWorker имеет следующие сигналы:
        1) progressStatus: Сигнал с информацией о прогрессе выполнения задачи (тип int).
        2) progressText: Сигнал с текстовой информацией о прогрессе выполнения задачи (тип str).
        3) taskFinished: Сигнал, который отправляется при завершении задачи.
    """

    progressStatus = pyqtSignal(int)
    progressText = pyqtSignal(str)
    taskFinished = pyqtSignal()

    def __init__(self, options: dict):
        """Конструктор класса FileWorker."""

        super().__init__()
        self.request = None
        self.region = None
        self.pages = None
        self.area_id = None
        self.period = None
        self.order_by = None
        self.only_with_salary = None

        for attr_name, value in options.items():
            self.__setattr__(attr_name, value)

    @staticmethod
    def get_path() -> str:
        """
        Статический метод, который создаёт директорию для хранения файлов и возвращает её.

        :return: Путь до директории с файлами.
        """

        directory = r'../Мои запросы/'
        if not path.exists(directory):
            mkdir(directory)
        return directory

    def create_workbook(self) -> CustomWorkbook:
        """
        Метод создает книгу Excel и возвращает ее объект.

        :return: Объект книги Excel.
        """

        directory = self.get_path()
        return CustomWorkbook(directory, self.request, self.region)

    @staticmethod
    def create_sheets(workbook: CustomWorkbook) -> tuple:
        """
        Метод создаёт листы в книге Excel и возвращает их объекты.

        :param workbook: Объект книги Excel.

        :return: Кортеж из объектов листов Excel.
        """

        ws_1 = CustomWorksheet('Вакансии', workbook)
        ws_2 = CustomWorksheet('Навыки_табл', workbook)
        ws_3 = CustomWorksheet('Зарплата_табл', workbook)
        ws_4 = CustomWorksheet('Удалёнка_табл', workbook)
        return ws_1, ws_2, ws_3, ws_4

    @staticmethod
    def hide_data_sheets(*sheets: CustomWorksheet):
        """
        Метод скрывает листы с данными в Excel файле, так как они будут представлены на диаграммах.

        :param sheets: Переменное количество объектов листов Excel, которые необходимо скрыть.
        """

        for s in sheets:
            s.hide()

    @staticmethod
    def format_main_table(table: CustomWorksheet, formats_from: CustomWorkbook):
        """
        Форматирует главную таблицу.

        :param table: Объект кастомного листа (сводная таблица данных).
        :param formats_from: Объект, предоставляющий необходимые форматы для ячеек таблицы.
        """

        headlines_format, string_format, numbers_format, days_format = formats_from.make_cells_formats()
        table.add_headlines(headlines_format)
        table.set_cell_formats(string_format, numbers_format, days_format)
        table.add_conditional_formatting()
        table.freeze_panes(1, 0)
        table.cut_unused_cells(col=9)

    def write_data(self, table: CustomWorksheet, *others: CustomWorksheet):
        """
        Заполняет все таблицы собранными данными.

        :param table: Объект кастомного листа (главная таблица).
        :param others: Дополнительные листы, в которые будут записаны данные (навыки, зарплата, удаленка).
        """

        parser.parse_page(self.request,
                          self.area_id,
                          self.pages,
                          self.period,
                          self.only_with_salary,
                          self.order_by,
                          table,
                          worker=self)

        salaries, skills = parser.get_collected_data()

        others[0].write_skills(skills)
        others[1].write_salary_statistics(salaries)
        others[2].write_remote_data()

    @staticmethod
    def create_charts(workbook: CustomWorkbook):
        """
        Создает диаграммы для полученных данных.

        :param workbook: Объект книги Excel.
        """

        workbook.create_bar_chart('Навыки')
        workbook.create_column_chart('Зарплата')
        workbook.create_pie_chart('Удалёнка')

    def close_workbook(self, workbook: CustomWorkbook):
        """
        Закрывает книгу и завершает процесс работы.

        :param workbook: Объект книги Excel.
        """

        workbook.close()
        print(f'Файл {self.request} закрыт.')
        self.taskFinished.emit()

    def run(self):
        """Запускает процесс формирования и заполнения книги Excel."""

        workbook = self.create_workbook()

        main_table, *charts = self.create_sheets(workbook)

        self.hide_data_sheets(*charts)

        self.format_main_table(main_table, formats_from=workbook)

        self.write_data(main_table, *charts)

        self.create_charts(workbook)

        self.close_workbook(workbook)
