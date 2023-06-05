from collections import Counter
from parser_hh import skills_list


def write_skills(ws, n):
    ws.set_column('A:A', 30)

    row = 2
    for data in reversed(Counter(skills_list).most_common(n)):
        ws.write_row(f'A{row}', data)
        row += 1


def create_bar_chart(wb, chart_name, vacancy_name, n):
    chartsheet = wb.add_chartsheet(chart_name)
    chart = wb.add_chart({'type': 'bar'})
    chartsheet.set_chart(chart)

    chart.add_series({'name': '=Skills_data!$B$1',
                      'categories': f'=Skills_data!A2:A{n + 1}',
                      'values': f'=Skills_data!B2:B{n + 1}'})

    chart.set_title({'name': f'Топ-{n} навыков: {vacancy_name}'})
    chart.set_x_axis({'name': 'Частота'})

    chart.set_style(7)
