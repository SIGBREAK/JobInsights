def write_schedule_data(ws, remote, total):
    ws.write_row("A1", ("Удалёнка", remote))
    ws.write_row("A2", ("Офис", total - remote))


def create_pie_chart(wb, chart_name, vacancy_name):
    chartsheet = wb.add_chartsheet(chart_name)
    chart = wb.add_chart({"type": "pie"})
    chartsheet.set_chart(chart)

    chart.add_series(
        {"categories": '=Удалёнка_табл!A1:A2',
         "values": '=Удалёнка_табл!B1:B2'})

    chart.set_title({"name": f"Формат работы: {vacancy_name}"})
    chart.set_style(10)
