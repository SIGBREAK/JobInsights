from parser import salaries_list
from statistics import mean, median, mode


def write_salary_statistics(ws, data=None):
    functions = {'Минимальная': min,
                 'Медианная': median,
                 'Средняя': mean,
                 'Модальная': mode,
                 'Максимальная': max}

    if not data:
        data = salaries_list

    ws.set_column('A:A', 30)
    ws.write('A1', 'Зарплата')

    for row, f_name in enumerate(functions, 2):
        ws.write_row(f'A{row}', (f_name, int(functions[f_name](data))))


def create_column_chart(wb, chart_name, vacancy_name):
    chartsheet = wb.add_chartsheet(chart_name)
    chart = wb.add_chart({"type": "column"})
    chartsheet.set_chart(chart)

    chart.add_series({'categories': '=Зарплата_табл!A2:A6',
                      'values': '=Зарплата_табл!B2:B6'})

    chart.set_title({'name': f'Показатели зарплаты: {vacancy_name}'})
