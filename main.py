import remote
import salary
import skills

from formatter import *
from parser import parse_page


# Ввод пользовательских значений
pages_number = 1
skills_number = 20
my_request = 'Разработчик'

# Создание файла Excel
path = get_path()
wb_1 = CustomWorkbook(path, my_request)

# Создание листов
ws_1 = wb_1.add_worksheet('Вакансии')
ws_2 = wb_1.add_worksheet('Навыки_табл')
ws_3 = wb_1.add_worksheet('Зарплата_табл')
ws_4 = wb_1.add_worksheet('Удалёнка_табл')

# Таблицы 2,3,4 - вспомогательные и должны быть скрыты
ws_2.hide()
ws_3.hide()
ws_4.hide()

# Форматирование результирующей таблицы
headlines = ['Должность', 'ЗП от (чист.),\nруб', 'ЗП до (чист.),\nруб', 'Минимум опыта\nлет ',
             'Удалёнка', 'Опубликовано\n(дней)', 'Создано\n(дней)', 'Компания', 'Подробнее']
headlines_format, string_format, numbers_format, days_format = wb_1.add_cells_formatting()
add_headlines(ws_1, headlines, headlines_format)
set_cell_formats(ws_1, string_format, numbers_format, days_format)
add_conditional_formatting(ws_1)
ws_1.freeze_panes(1, 0)
cut_unused_cells(ws_1, col=9)

# Запись данных о вакансиях в таблицу
parse_page(my_request, pages_number, sheet=ws_1)

# Создание диаграммы требуемых навыков
skills.write_skills(ws_2, skills_number)
skills.create_bar_chart(wb_1, 'Навыки', my_request, skills_number)

# Создание диаграммы уровня заработной платы
salary.write_salary_statistics(ws_3)
salary.create_column_chart(wb_1, 'Зарплата', my_request)

# Создание диаграммы формата работы
remote.write_remote_data(ws_4)
remote.create_pie_chart(wb_1, 'Удалёнка', my_request)

# Закрытие файла
wb_1.close()
print('Файл закрыт')
