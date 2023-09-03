# /* coding: UTF-8 */

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QLineEdit, QCompleter,
                             QPushButton, QSlider, QLabel, QProgressBar, QMainWindow, QCheckBox, QComboBox)

from images import icon
from .api import areas, get_my_area_id, get_page, vacancy_search_order
from .parser import parser
from .worker import FileWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.areas_dict = areas

        # Название программы и размеры окна
        self.setWindowTitle('JobInsights (RU)')
        self.setWindowIcon(icon('pie_chart.png'))
        self.setFixedSize(500, 350)

        # Окно ввода вакансии
        self.job_field = QLineEdit(self)
        self.job_field.setPlaceholderText('Профессия')
        self.job_field.setGeometry(10, 30, 380, 30)
        self.job_field.setFont(QFont("Arial", 14))

        # Кнопка начать поиск
        self.search_button = QPushButton(icon('search.png'), '', self)
        self.search_button.setGeometry(400, 30, 45, 30)

        # Кнопка СТОП
        self.stop_button = QPushButton(icon('cancel.png'), '', self)
        self.stop_button.setGeometry(445, 30, 45, 30)
        self.stop_button.setEnabled(False)

        # Надпись Регион:
        self.region = QLabel('Регион:', self)
        self.region.setGeometry(10, 80, 40, 20)

        # Выбор региона
        self.area_box = QLineEdit(self)
        self.area_box.setPlaceholderText('Все регионы')
        self.area_box.setGeometry(60, 80, 200, 20)
        suggestions = self.areas_dict.values()  # Тут подхватываются города из инициализатора API hh.ru
        completer = QCompleter(suggestions, self.area_box)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.area_box.setCompleter(completer)

        # Слайдер и количество анализируемых страниц
        self.pages_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.pages_slider.setGeometry(10, 260, 250, 20)
        self.pages_slider.setMinimum(1)
        self.pages_slider.setMaximum(20)
        self.pages_slider.setValue(10)

        self.pages_display = QLabel(f'Число страниц поиска: {self.pages_slider.value()}', self)
        self.pages_display.setGeometry(10, 280, 180, 20)
        self.pages_display.setFont(QFont('Arial', 11))

        # Статус строка внизу справа
        self.status_label = QLabel('Статус: Ожидание', self)
        self.status_label.setGeometry(280, 260, 210, 45)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Шкала прогресса поиска
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, 310, 480, 30)
        self.progress_bar.setMaximum(100)

        # Названия вакансий, меняющиеся в шкале прогресса
        self.vacancy_label = QLabel('', self)
        self.vacancy_label.setGeometry(20, 310, 480, 30)
        vacancy_font = QFont()
        vacancy_font.setItalic(True)
        self.vacancy_label.setFont(vacancy_font)

        # Галочка отсева вакансий без указания дохода
        self.salary_button = QCheckBox('Только с указанием дохода', self)
        self.salary_button.setGeometry(10, 110, 230, 20)
        self.salary_button.isChecked()

        # Подпись для сортировки
        self.order_by_label = QLabel('Сортировать:', self)
        self.order_by_label.setGeometry(10, 140, 90, 20)

        # Выпадающий список сортировки
        self.order_by_box = QComboBox(self)
        self.order_by_box.addItems(vacancy_search_order)
        self.order_by_box.setGeometry(95, 140, 165, 20)

        # Подпись для периода публикации
        self.period_label = QLabel(f'Только вакансии за последние{" ".center(19)}дней.', self)
        self.period_label.setGeometry(10, 230, 250, 20)

        # Вписать значение периода публикации
        self.period_box = QLineEdit(self)
        self.period_box.setPlaceholderText('365')
        self.period_box.setGeometry(190, 230, 30, 20)

        # Связывание виджетов с функциями
        self.pages_slider.valueChanged.connect(self.update_pages_number)
        self.search_button.clicked.connect(self.search)
        self.stop_button.clicked.connect(parser.stop_parsing)

    def update_pages_number(self, value: int):
        """
        Обновляет отображаемое значение числа анализируемых страниц поиска при движении слайдера.

        :param value: Новое значение числа страниц.
        """

        self.pages_display.setText(f'Число страниц поиска: {value}')

    def update_progress_bar(self, value: int):
        """
        Обновляет значение шкалы прогресса.

        :param value: Значение прогресса (от 0 до 100).
        """

        self.progress_bar.setValue(value)

    def update_progress_text(self, vacancy_name: str):
        """
        Обновляет название вакансии, отображаемое в шкале прогресса.

        :param vacancy_name: Название текущей обрабатываемой вакансии.
        """

        self.vacancy_label.setText(vacancy_name)

    def unlock_buttons(self, key):
        """
        Разблокирует или блокирует кнопки и поля ввода в зависимости от значения ключа.

        :param key: Значение True разблокирует элементы (кроме кнопки СТОП), False - блокирует (также кроме СТОП).
        """

        self.search_button.setEnabled(key)
        self.job_field.setEnabled(key)
        self.area_box.setEnabled(key)
        self.pages_slider.setEnabled(key)
        self.salary_button.setEnabled(key)
        self.order_by_box.setEnabled(key)
        self.period_box.setEnabled(key)
        self.stop_button.setEnabled(not key)

    def searching_completed(self):
        """Вызывается по завершении процесса поиска вакансий и обновляет интерфейс после завершения работы."""

        self.unlock_buttons(key=True)
        self.vacancy_label.setText('')
        self.progress_bar.setValue(0)
        self.status_label.setText(f'Статус: Файл создан.\nПоиск завершён.')

    def period_edit(self):
        """Возвращает валидное значение числа дней, за которое могли быть опубликованы вакансии."""

        try:
            value = int(self.period_box.text())
            if 0 < value <= 365:
                return value
        except ValueError:
            pass
        self.period_box.setText('365')
        return 365

    def search(self):
        """Запускает процесс поиска вакансий и создания книги Excel."""

        request = self.job_field.text()
        region = self.area_box.text()
        area_id = get_my_area_id(region, self.areas_dict)
        pages = self.pages_slider.value()
        period = self.period_edit()
        order_by = vacancy_search_order[self.order_by_box.currentText()]
        only_with_salary = self.salary_button.isChecked()

        _, found = get_page(request, area_id, period, only_with_salary)
        if not request or not found:
            self.status_label.setText(f"Статус: Не найдено вакансий.")
            return

        options = {'request': request,
                   'region': region,
                   'area_id': area_id,
                   'pages': pages,
                   'period': period,
                   'order_by': order_by,
                   'only_with_salary': only_with_salary}

        # Создаём тред для поиска вакансий
        self.unlock_buttons(key=False)
        self.status_label.setText(f"Статус: Идёт поиск.\nПо запросу найдено {found} вакансий.")
        self.worker = FileWorker(options=options)

        self.worker.progressStatus.connect(self.update_progress_bar)
        self.worker.progressText.connect(self.update_progress_text)
        self.worker.taskFinished.connect(self.searching_completed)
        self.worker.start()
