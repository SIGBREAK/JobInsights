from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QCompleter,
                             QPushButton, QStyle, QSlider, QLabel, QProgressBar)
from PyQt5.QtGui import QPalette, QColor, QFont


class ParserInterface(QWidget):
    def __init__(self, class_worker, object_parser):
        super().__init__()
        self._class_worker = class_worker
        self._object_parser = object_parser
        self._areas_dict = self._object_parser.init_areas_dict()

        self.setWindowTitle('hh_insights')
        self.setFixedSize(500, 235)

        # Окно ввода вакансии
        self.job_field = QLineEdit('Python разработчик', self)
        self.job_field.setGeometry(10, 30, 380, 30)
        self.job_field.setFont(QFont("Arial", 14))

        # Кнопка начать поиск
        self.search_button = QPushButton(self)
        self.search_button.setGeometry(400, 30, 45, 30)
        self.search_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogContentsView')))

        # Кнопка СТОП
        self.stop_button = QPushButton(self)
        self.stop_button.setGeometry(445, 30, 45, 30)
        self.stop_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxCritical')))
        self.stop_button.setEnabled(False)

        # Надпись Регион:
        self.region = QLabel('Регион:', self)
        self.region.setGeometry(10, 80, 40, 20)

        # Выбор региона
        self.area_box = QLineEdit('Москва', self)
        self.area_box.setGeometry(60, 80, 200, 20)
        suggestions = self._areas_dict.values()  # Тут подхватываются города из инициализатора API hh.ru
        completer = QCompleter(suggestions, self.area_box)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.area_box.setCompleter(completer)

        # Слайдер и количество анализируемых страниц
        self.pages_slider = QSlider(Qt.Horizontal, self)
        self.pages_slider.setGeometry(10, 150, 180, 20)
        self.pages_slider.setMinimum(1)
        self.pages_slider.setMaximum(20)
        self.pages_slider.setValue(10)

        self.pages_display = QLabel(f'Число страниц поиска: {self.pages_slider.value()}', self)
        self.pages_display.setGeometry(10, 170, 180, 20)
        self.pages_display.setFont(QFont('Arial', 11))

        # Статус строка внизу справа
        self.status_label = QLabel('Статус: Ожидание', self)
        self.status_label.setGeometry(280, 150, 210, 45)

        # Шкала прогресса поиска
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, 200, 480, 30)
        self.progress_bar.setMaximum(100)

        # Связывание наших кнопок с функциями
        self.pages_slider.valueChanged.connect(self.update_pages_number)
        self.search_button.clicked.connect(self.search)
        self.stop_button.clicked.connect(self._object_parser.stop_searching)

    def update_pages_number(self, value):
        self.pages_display.setText(f'Число страниц поиска: {value}')

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def searching_completed(self):
        self.search_button.setEnabled(True)
        self.job_field.setEnabled(True)
        self.area_box.setEnabled(True)
        self.pages_slider.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText(f'Статус: Файл создан.\nПоиск завершён.')

    def search(self):
        my_request = self.job_field.text()
        my_region = self.area_box.text()
        pages_number = self.pages_slider.value()
        my_area_id = self._object_parser.get_my_area_id(my_region, self._areas_dict)

        # Отсечка на создание треда при отсутствии вакансий/ запроса
        vacancies = self._object_parser.get_page(my_request, my_area_id)

        if not vacancies['found'] or not my_request:
            self.status_label.setText(f"Статус: Не найдено вакансий.")
            return

        # Создаём тред для поиска вакансий
        self.search_button.setEnabled(False)
        self.job_field.setEnabled(False)
        self.area_box.setEnabled(False)
        self.pages_slider.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText(f"Статус: Идёт поиск.\nПо запросу найдено {vacancies['found']} вакансий.")
        self.worker = self._class_worker(my_request, my_region, pages_number, self._areas_dict, self._object_parser, self)
        self.worker.finished.connect(self.searching_completed)
        self.worker.start()
