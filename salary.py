from parser import salaries_list
from statistics import mean, median, mode

functions = {'Минимальная': min,
             'Медианная': median,
             'Средняя': mean,
             'Модальная': mode,
             'Максимальная': max}


def write_salary_statistics(ws, data=None):
    if not data:
        data = salaries_list

    ws.set_column('A:A', 30)
    ws.write('A1', 'Зарплата')

    count = 2
    for name, func in functions.items():
        ws.write_row(f'A{count}', (name, func(data)))
        count += 1


def create_column_chart(wb, chart_name, vacancy_name):
    chartsheet = wb.add_chartsheet(chart_name)
    chart = wb.add_chart({"type": "column"})
    chartsheet.set_chart(chart)

    chart.add_series({'categories': '=Salary_data!A2:A6',
                      'values': '=Salary_data!B2:B6'})

    chart.set_title({'name': f'Показатели зарплаты: {vacancy_name}'})
