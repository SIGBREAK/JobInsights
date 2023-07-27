from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QLineEdit, QCompleter,
                             QPushButton, QStyle, QSlider, QLabel, QProgressBar, QMainWindow)
from .api import areas_dict, get_my_area_id, check_for_vacancies
from .worker import FileWorker
from .parser import Parser


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.areas_dict = areas_dict

        self.init_user_interface()

    def init_user_interface(self):
        # Название программы и размеры окна
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
        self.area_box = QLineEdit(self)
        self.area_box.setPlaceholderText('Россия')
        self.area_box.setGeometry(60, 80, 200, 20)
        suggestions = self.areas_dict.values()  # Тут подхватываются города из инициализатора API hh.ru
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
        self.status_label.setAlignment(Qt.AlignRight)

        # Шкала прогресса поиска
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, 200, 480, 30)
        self.progress_bar.setMaximum(100)

        # Названия вакансий, меняющиеся в шкале прогресса
        self.vacancy_label = QLabel('', self)
        self.vacancy_label.setGeometry(20, 200, 480, 30)
        vacancy_font = QFont()
        vacancy_font.setItalic(True)
        self.vacancy_label.setFont(vacancy_font)

        # Связывание наших кнопок с функциями
        self.pages_slider.valueChanged.connect(self.update_pages_number)
        self.search_button.clicked.connect(self.search)
        self.stop_button.clicked.connect(Parser.stop_parsing)

    def update_pages_number(self, value):
        self.pages_display.setText(f'Число страниц поиска: {value}')

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def update_progress_text(self, vacancy_name):
        self.vacancy_label.setText(vacancy_name)

    def unlock_buttons(self, key):
        self.search_button.setEnabled(key)
        self.job_field.setEnabled(key)
        self.area_box.setEnabled(key)
        self.pages_slider.setEnabled(key)
        self.stop_button.setEnabled(not key)

    def searching_completed(self):
        self.unlock_buttons(key=True)
        self.vacancy_label.setText('')
        self.progress_bar.setValue(0)
        self.status_label.setText(f'Статус: Файл создан.\nПоиск завершён.')

    def search(self):
        my_request = self.job_field.text()
        my_region = 'Россия' if not self.area_box.text() else self.area_box.text()
        pages_number = self.pages_slider.value()
        area_id = get_my_area_id(my_region, self.areas_dict)

        found = check_for_vacancies(my_request, area_id)
        if not found:
            self.status_label.setText(f"Статус: Не найдено вакансий.")
            return

        # Создаём тред для поиска вакансий
        self.unlock_buttons(key=False)
        self.status_label.setText(f"Статус: Идёт поиск.\nПо запросу найдено {found} вакансий.")
        self.worker = FileWorker(my_request, my_region, area_id, pages_number)

        self.worker.progressStatus.connect(self.update_progress_bar)
        self.worker.progressText.connect(self.update_progress_text)
        self.worker.taskFinished.connect(self.searching_completed)
        self.worker.start()
