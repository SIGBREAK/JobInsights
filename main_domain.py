import formatter as f
from parser_hh import parse_page, get_schedule
import skills_chart as s
from salary_data import write_salary_statistics, create_column_chart
import remote_chart as r

# Ввод пользовательских значений
pages_number = 1
skills_number = 20
my_request = 'Водитель'


# Создание Excel и предварительное форматирование
path = f.get_path()
excel = f.create_excel(path, my_request)

headlines_format, string_format, numbers_format, days_format = f.add_cells_formatting(excel)

ws1 = f.create_worksheet(excel, 'All_vacancies_data')
headings = ['Должность', 'ЗП от (чист.),\nруб', 'ЗП до (чист.),\nруб', 'Минимум опыта\nлет ',
            'Удалёнка', 'Опубликовано\n(дней)', 'Создано\n(дней)', 'Компания', 'Подробнее']
f.add_headlines(ws1, headings, headlines_format)
f.set_cell_formats(ws1, string_format, numbers_format, days_format)
f.add_conditional_formatting(ws1)
f.freeze_first_row(ws1)

# Парсинг страниц с записью данных о вакансиях
parse_page(my_request, pages_number, write_to=ws1)
print('Вакансии собраны')
f.cut_unused_cells(ws1, col=9)

# Запись данных о ключевых навыках
ws2 = f.create_worksheet(excel, 'Skills_data')
f.add_headlines(ws2, ['Навык', 'Частота'])
f.freeze_first_row(ws2)

s.write_skills(ws2, skills_number)
s.create_bar_chart(excel, 'Skills_chart', my_request, skills_number)

f.cut_unused_cells(ws2, col=2)

# Вычисление статистических показателей и запись данных о ЗП
ws3 = f.create_worksheet(excel, 'Salary_data')
write_salary_statistics(ws3)

f.cut_unused_cells(ws3, col=2)

create_column_chart(excel, 'Salary_chart', my_request)

# Определение удалённых вакансий и построение графика
ws4 = f.create_worksheet(excel, 'Remote_data')
r.write_schedule_data(ws4, *get_schedule())
r.create_pie_chart(excel, 'Remote_chart', my_request)

f.cut_unused_cells(ws4, col=2)

# Закрытие файла
excel.close()
print('Файл закрыт')
