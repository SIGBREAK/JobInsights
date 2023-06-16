def write_remote_data(ws):
    ws.write('A1', 'Удалёнка')
    ws.write_formula('B1', f'=SUM(Вакансии!E:E)')

    ws.write('A2', 'Офис')
    ws.write_formula('B2', f'=COUNTA(Вакансии!E:E) - SUM(Вакансии!E:E) - 1')


def create_pie_chart(wb, chart_name, vacancy_name):
    chartsheet = wb.add_chartsheet(chart_name)
    chart = wb.add_chart({"type": "pie"})
    chartsheet.set_chart(chart)

    labels_options = {'percentage': True,
                      'font': {'name': 'Arial',
                               'size': 14,
                               'bold': True,
                               'color': 'white'},
                      'position': 'center'}

    pie_chart_colors = [{"fill": {"color": "#00B0F0"}},
                        {"fill": {"color": "#17375E"}}]

    title_font = {'name': 'Times New Roman', 'size': 17}

    chart.add_series({"categories": '=Удалёнка_табл!A1:A2',
                      "values": '=Удалёнка_табл!B1:B2',
                      'data_labels': labels_options,
                      "points": pie_chart_colors})

    chart.set_title({"name": f"Формат работы: {vacancy_name}",
                     'name_font': title_font})

    chart.set_legend({'position': 'top'})
