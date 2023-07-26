from string import ascii_uppercase
from xlsxwriter import Workbook


class CustomWorkbook(Workbook):
    def __init__(self, f_path, request, region):
        super().__init__(rf'{f_path}{request} ({region}).xlsx', {'constant_memory': True})

    def add_cells_formatting(self):
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


class CustomWorksheet:
    def __init__(self, name, workbook_object):
        # Вызываем метод add_worksheet() из объекта CustomWorkbook для создания листа
        self.worksheet = workbook_object.add_worksheet(name)

    def __getattr__(self, attr):
        # Если атрибут не найден в кастомном классе, делегируем вызов к объекту worksheet
        return getattr(self.worksheet, attr)

    def add_headlines(self, headings, headings_format):
        self.write_row('A1', headings, headings_format)

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
