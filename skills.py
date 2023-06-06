from collections import Counter
from parser import skills_list


def write_skills(ws, n):
    ws.set_column('A:A', 30)
    skills_data = reversed(Counter(skills_list).most_common(n))

    for row, data in enumerate(skills_data, 1):
        ws.write_row(f'A{row}', data)


def create_bar_chart(wb, chart_name, vacancy_name, n):
    chartsheet = wb.add_chartsheet(chart_name)
    chart = wb.add_chart({'type': 'bar'})
    chartsheet.set_chart(chart)

    chart.add_series({'name': '=Навыки_табл!$B$1',
                      'categories': f'=Навыки_табл!A1:A{n}',
                      'values': f'=Навыки_табл!B1:B{n}',
                      'data_labels': {'value': True},
                      'fill': {'color': 'blue'},
                      'gradient': {'colors': ['#99CCFF', '#0066FF'], 'angle': 45}
                      })

    chart.set_title({'name': f'Топ-{n} навыков: {vacancy_name}',
                     'font': {'size': 15}})

    chart.set_x_axis({'name': 'Частота',
                      'name_font': {'size': 12, 'name': 'Times New Roman', 'bold': False},
                      'num_format': '# ###', 'num_font': {'size': 12, 'name': 'Times New Roman'}})

    chart.set_y_axis({'num_font': {'size': 12, 'name': 'Times New Roman'}})

    chart.set_legend({'none': True})
