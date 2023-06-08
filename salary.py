from parser import salaries_list
from statistics import mean, median, mode


def write_salary_statistics(ws, data=None):
    functions = {'Медианная': median,
                 'Средняя': mean,
                 'Модальная': mode}

    if not data:
        data = salaries_list

    ws.set_column('A:A', 30)
    ws.write('A1', 'Зарплата')

    for row, f_name in enumerate(functions, 2):
        ws.write_row(f'A{row}', (f_name, int(functions[f_name](data))))

    ws.write_row('A5', ('Минимальная', '=MIN(Вакансии!B:B, Вакансии!C:C)'))
    ws.write_row('A6', ('Максимальная', '=MAX(Вакансии!B:B, Вакансии!C:C)'))


def create_column_chart(wb, chart_name, vacancy_name):
    chartsheet = wb.add_chartsheet(chart_name)
    chart = wb.add_chart({"type": "column"})
    chartsheet.set_chart(chart)

    labels_options = {'value': True,
                      'font': {'name': 'Arial',
                               'size': 12,
                               'bold': True,
                               'color': 'white'},
                      'position': 'inside_end',
                      'num_format': '# ### ### ₽'}

    axis_font = {'name': 'Times New Roman', 'size': 12}
    title_font = {'name': 'Times New Roman', 'size': 17}

    chart.add_series({'categories': '=Зарплата_табл!A2:A6',
                      'values': '=Зарплата_табл!B2:B6',
                      'data_labels': labels_options,
                      'fill': {'color': 'blue'},
                      'gradient': {'colors': ['#17375E', '#00B0F0'],
                                   'angle': 90},
                      'gap': 40})

    chart.set_x_axis({'num_font': axis_font})

    chart.set_y_axis({'num_format': '# ### ###',
                      'num_font': axis_font})

    chart.set_title({'name': f'Показатели зарплаты: {vacancy_name}',
                     'name_font': title_font})

    chart.set_legend({'none': True})
