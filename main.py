from formatter import *
from parser import parse_page, get_schedule
import skills as s
from salary import write_salary_statistics, create_column_chart
import remote as r

# Ввод пользовательских значений
pages_number = 1
skills_number = 20
my_request = 'Разработчик'


# Создание файла Excel
path = get_path()
wb_1 = CustomWorkbook(path, my_request)

# Создание листов
ws_1 = wb_1.add_worksheet('All_vacancies_data')
ws_2 = wb_1.add_worksheet('Skills_data')
ws_3 = wb_1.add_worksheet('Salary_data')
ws_4 = wb_1.add_worksheet('Remote_data')

# Таблицы 2,3,4 - вспомогательные и должны быть скрыты
ws_2.hide()
ws_3.hide()
ws_4.hide()

# Форматирование результирующей таблицы
headlines_format, string_format, numbers_format, days_format = wb_1.add_cells_formatting()
headings = ['Должность', 'ЗП от (чист.),\nруб', 'ЗП до (чист.),\nруб', 'Минимум опыта\nлет ',
            'Удалёнка', 'Опубликовано\n(дней)', 'Создано\n(дней)', 'Компания', 'Подробнее']
add_headlines(ws_1, headings, headlines_format)
set_cell_formats(ws_1, string_format, numbers_format, days_format)
add_conditional_formatting(ws_1)
ws_1.freeze_panes(1, 0)
cut_unused_cells(ws_1, col=9)

# Запись данных о вакансиях в таблицу
parse_page(my_request, pages_number, write_to=ws_1)

# Создание диаграммы требуемых навыков
add_headlines(ws_2, ['Навык', 'Частота'])
s.write_skills(ws_2, skills_number)
s.create_bar_chart(wb_1, 'Skills_chart', my_request, skills_number)

# Создание диаграммы уровня заработной платы
write_salary_statistics(ws_3)
create_column_chart(wb_1, 'Salary_chart', my_request)

# Создание диаграммы формата работы
r.write_schedule_data(ws_4, *get_schedule())
r.create_pie_chart(wb_1, 'Remote_chart', my_request)

# Закрытие файла
wb_1.close()
print('Файл закрыт')
