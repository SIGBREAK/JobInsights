from string import ascii_uppercase
from xlsxwriter import Workbook
from statistics import mean, median, mode
from collections import Counter
from .parser import Parser


class CustomWorkbook(Workbook):
    def __init__(self, f_path, request, region):
        super().__init__(rf'{f_path}{request} ({region}).xlsx', {'constant_memory': True})
        self.request = request
        self.region = region

    def make_cells_formats(self):
        headlines_format = self.add_format({'bold': True,
                                            'font_size': 13,
                                            'align': 'center',
                                            'font_name': 'Times New Roman',
                                            'text_wrap': True})

        string_format = self.add_format({'font_size': 11,
                                         'font_name': 'Times New Roman'})

        numbers_format = self.add_format({'align': 'center',
                                          'font_size': 11,
                                          'num_format': '# ### ###',
                                          'font_name': 'Times New Roman'})

        days_format = self.add_format({'align': 'center',
                                       'font_size': 11,
                                       'num_format': 1,
                                       'font_name': 'Times New Roman'})

        headlines_format.set_align('vcenter')

        return headlines_format, string_format, numbers_format, days_format

    def create_column_chart(self, chart_name):
        chartsheet = self.add_chartsheet(chart_name)
        chart = self.add_chart({"type": "column"})
        chartsheet.set_chart(chart)

        labels_options = {'value': True,
                          'font': {'name': 'Arial',
                                   'size': 12,
                                   'bold': True,
                                   'color': 'white'},
                          'position': 'inside_end',
                          'num_format': '# ### ### ₽'}

        axis_options = {'num_format': '# ### ###',
                        'num_font': {'name': 'Times New Roman', 'size': 12}}

        title_font = {'name': 'Times New Roman', 'size': 15}

        chart.add_series({'categories': '=Зарплата_табл!A2:A6',
                          'values': '=Зарплата_табл!B2:B6',
                          'data_labels': labels_options,
                          'fill': {'color': 'blue'},
                          'gradient': {'colors': ['#17375E', '#00B0F0'],
                                       'angle': 90},
                          'gap': 40})

        labels_options['font']['color'] = 'black'
        chart.add_series({'categories': '=Зарплата_табл!A2:A6',
                          'values': '=Зарплата_табл!C2:C6',
                          'data_labels': labels_options,
                          'fill': {'color': 'blue'},
                          'gradient': {'colors': ['#EE8E00', '#FFE36D'],
                                       'angle': 90},
                          'y2_axis': True,
                          'gap': 40})

        chart.set_x_axis(axis_options)
        chart.set_y_axis(axis_options)
        chart.set_y2_axis(axis_options)

        chart.set_title({'name': f'Показатели заработной платы: {self.request}\n({self.region})',
                         'name_font': title_font})

        chart.set_legend({'none': True})

    def create_bar_chart(self, chart_name):
        chartsheet = self.add_chartsheet(chart_name)
        chart = self.add_chart({'type': 'bar'})
        chartsheet.set_chart(chart)

        labels_options = {'value': True,
                          'font': {'italic': True}}

        axis_font = {'name': 'Times New Roman', 'size': 12, 'bold': False}
        title_font = {'name': 'Times New Roman', 'size': 15}

        chart.add_series({'categories': f'=Навыки_табл!A1:A20',
                          'values': f'=Навыки_табл!B1:B20',
                          'data_labels': labels_options,
                          'fill': {'color': 'blue'},
                          'gradient': {'colors': ['#22518A', '#00C0F0'],
                                       'angle': 180},
                          'gap': 80})

        chart.set_title({'name': f'Топ-20 навыков: {self.request}\n({self.region})',
                         'name_font': title_font})

        chart.set_x_axis({'name': 'Частота',
                          'name_font': axis_font,
                          'num_format': '# ###',
                          'num_font': axis_font})

        chart.set_y_axis({'num_font': axis_font})

        chart.set_legend({'none': True})

    def create_pie_chart(self, chart_name):
        chartsheet = self.add_chartsheet(chart_name)
        chart = self.add_chart({"type": "pie"})
        chartsheet.set_chart(chart)

        labels_options = {'percentage': True,
                          'category': True,
                          'font': {'name': 'Arial',
                                   'size': 14,
                                   'bold': True,
                                   'color': 'white'},
                          'position': 'center'}

        pie_chart_colors = [{"fill": {"color": "#00B0F0"}},
                            {"fill": {"color": "#17375E"}}]

        title_font = {'name': 'Times New Roman', 'size': 15}

        chart.add_series({"categories": '=Удалёнка_табл!A1:A2',
                          "values": '=Удалёнка_табл!B1:B2',
                          'data_labels': labels_options,
                          "points": pie_chart_colors})

        chart.set_title({"name": f"Формат работы: {self.request}\n({self.region})",
                         'name_font': title_font})

        chart.set_legend({'none': True})


class CustomWorksheet:
    def __init__(self, name, workbook_object):
        # Вызываем метод add_worksheet() из объекта CustomWorkbook для создания листа
        self.worksheet = workbook_object.add_worksheet(name)

    def __getattr__(self, attr):
        # Если атрибут не найден в кастомном классе, делегируем вызов к объекту worksheet
        return getattr(self.worksheet, attr)

    def add_headlines(self, headings_format):
        headlines = ['Должность', 'ЗП (на руки) от, ₽', 'ЗП (на руки) до, ₽', 'Минимум опыта\nлет ',
                     'Удалёнка', 'Опубликовано\n(дней)', 'Создано\n(дней)', 'Компания', 'Подробнее']
        self.write_row('A1', headlines, headings_format)

    def add_conditional_formatting(self):
        self.conditional_format('B2:B2000', {'type': '3_color_scale'})

        self.conditional_format('C2:C2000', {'type': '3_color_scale'})

        self.conditional_format('D2:D2000', {'type': 'data_bar',
                                             'bar_border_color': '#008AEF',
                                             'bar_color': '#008AEF'})

        self.conditional_format('E2:E2000', {'type': 'icon_set',
                                             'icon_style': '3_symbols_circled',
                                             'icons_only': True,
                                             'icons': [{'criteria': '>=', 'type': 'number', 'value': 1},
                                                       {'criteria': '>', 'type': 'number', 'value': 0},
                                                       {'criteria': '<=', 'type': 'number', 'value': 0}]})

    def set_cell_formats(self, strings, numbers, days):
        self.set_column('A:A', 75, strings)
        self.set_column('B:C', 20, numbers)
        self.set_column('D:D', 24, numbers)
        self.set_column('E:E', 11, numbers)
        self.set_column('F:F', 19, days)
        self.set_column('G:G', 11, days)
        self.set_column('H:H', 38, strings)
        self.set_column('I:I', 40, strings)

    def cut_unused_cells(self, col):
        self.set_default_row(hide_unused_rows=True)
        self.set_column(f'{ascii_uppercase[col]}:XFD', None, None, {'hidden': True})

    def write_salary_statistics(self, salaries_list):
        functions = {'Медианная': median,
                     'Средняя': mean,
                     'Модальная': mode}

        self.set_column('A:A', 30)
        self.write('A1', 'Зарплата')

        for row, f_name in enumerate(functions, 2):
            self.write_row(f'A{row}', (f_name, int(functions[f_name](salaries_list))))

        self.write_row('A5', ('Минимальная', '=MIN(Вакансии!B:B, Вакансии!C:C)'))
        self.write_row('A6', ('Максимальная', '', '=MAX(Вакансии!B:B, Вакансии!C:C)'))

    def write_skills(self, skills_list):
        self.set_column('A:A', 30)
        skills_data = reversed(Counter(skills_list).most_common(20))

        for row, data in enumerate(skills_data, 1):
            self.write_row(f'A{row}', data)

    def write_remote_data(self):
        self.write('A1', 'Удалёнка')
        self.write_formula('B1', f'=SUM(Вакансии!E:E)')

        self.write('A2', 'Офис')
        self.write_formula('B2', f'=COUNTA(Вакансии!E:E) - SUM(Вакансии!E:E) - 1')

    def write_all_data(self, vacancy, row):
        self.write_row(f'A{row}', list(vacancy.__dict__.values())[1:-1])
