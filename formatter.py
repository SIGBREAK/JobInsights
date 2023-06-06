from os import path, mkdir
import xlsxwriter
from string import ascii_uppercase


class CustomWorkbook(xlsxwriter.Workbook):
    def __init__(self, f_path, my_request):
        super().__init__(rf'{f_path}GET_{my_request}.xlsx', {'constant_memory': True})

    def add_cells_formatting(self):
        headlines_format = self.add_format({'bold': True,
                                            'font_size': 13,
                                            'align': 'center',
                                            'font_name': 'Times New Roman',
                                            'text_wrap': True})
        headlines_format.set_align('vcenter')
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
        return headlines_format, string_format, numbers_format, days_format


def get_path():
    directory = r'../Мои запросы/'
    if not path.exists(directory):
        mkdir(directory)
    return directory


def add_headlines(ws, headings, format=None):
    if not format:
        ws.write_row('A1', headings)
    else:
        ws.write_row('A1', headings, format)


def add_conditional_formatting(ws):
    ws.conditional_format('B2:B2000', {'type': '3_color_scale'})

    ws.conditional_format('C2:C2000', {'type': '3_color_scale'})

    ws.conditional_format('D2:D2000', {'type': 'data_bar',
                                       'bar_border_color': '#008AEF',
                                       'bar_color': '#008AEF'})

    ws.conditional_format('E2:E2000', {'type': 'icon_set',
                                       'icon_style': '3_symbols_circled',
                                       'icons_only': True})


def set_cell_formats(ws, strings, numbers, days):
    ws.set_column('A:A', 75, strings)
    ws.set_column('B:C', 20, numbers)
    ws.set_column('D:D', 24, numbers)
    ws.set_column('E:E', 11, numbers)
    ws.set_column('F:F', 19, days)
    ws.set_column('G:G', 11, days)
    ws.set_column('H:H', 38, strings)
    ws.set_column('I:I', 40, strings)


def cut_unused_cells(ws, col):
    ws.set_default_row(hide_unused_rows=True)
    ws.set_column(f'{ascii_uppercase[col]}:XFD', None, None, {'hidden': True})
