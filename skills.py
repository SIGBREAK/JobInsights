from parser import skills_list
from collections import Counter


def write_skills(ws, n):
    ws.set_column('A:A', 30)
    skills_data = reversed(Counter(skills_list).most_common(n))

    for row, data in enumerate(skills_data, 1):
        ws.write_row(f'A{row}', data)


def create_bar_chart(wb, chart_name, vacancy_name, n):
    chartsheet = wb.add_chartsheet(chart_name)
    chart = wb.add_chart({'type': 'bar'})
    chartsheet.set_chart(chart)

    labels_options = {'value': True,
                      'font': {'italic': True}}

    axis_font = {'name': 'Times New Roman', 'size': 12}
    title_font = {'name': 'Times New Roman', 'size': 17}

    chart.add_series({'categories': f'=Навыки_табл!A1:A{n}',
                      'values': f'=Навыки_табл!B1:B{n}',
                      'data_labels': labels_options,
                      'fill': {'color': 'blue'},
                      'gradient': {'colors': ['#22518A', '#00C0F0'],
                                   'angle': 180},
                      'gap': 80})

    chart.set_title({'name': f'Топ-{n} навыков: {vacancy_name}',
                     'name_font': title_font})

    chart.set_x_axis({'name': 'Частота',
                      'name_font': axis_font,
                      'num_format': '# ###',
                      'num_font': axis_font})

    chart.set_y_axis({'num_font': axis_font})

    chart.set_legend({'none': True})
