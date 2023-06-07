def write_remote_data(ws):
    ws.write('A1', 'Удалёнка')
    ws.write_formula('B1', f'=SUM(Вакансии!E:E)')

    ws.write('A2', 'Офис')
    ws.write_formula('B2', f'=COUNTA(Вакансии!E:E) - SUM(Вакансии!E:E) - 1')


def create_pie_chart(wb, chart_name, vacancy_name):
    chartsheet = wb.add_chartsheet(chart_name)
    chart = wb.add_chart({"type": "pie"})
    chartsheet.set_chart(chart)

    chart.add_series(
        {"categories": '=Удалёнка_табл!A1:A2',
         "values": '=Удалёнка_табл!B1:B2'})

    chart.set_title({"name": f"Формат работы: {vacancy_name}"})
    chart.set_style(10)
