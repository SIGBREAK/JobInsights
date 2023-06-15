import sys
import traceback
from PyQt5.QtWidgets import (QApplication, QMessageBox)

import page_parser
import worker
import interface


def log_uncaught_exceptions(ex_cls, ex, tb):
    """Функция, которая позволяет выводить (в консоль и отдельне окно) ошибки интерфейса, идущие мимо stderr"""
    text = f'{ex_cls.__name__}: {ex}:\n'
    text += ''.join(traceback.format_tb(tb))
    print(text)
    QMessageBox.critical(None, 'Ошибка!', text)
    sys.exit()


sys.excepthook = log_uncaught_exceptions

if __name__ == '__main__':
    parser = page_parser.Parser()
    app = QApplication([])
    parser_app = interface.MainWindow(worker.FileWorker, parser)
    parser_app.show()
    sys.exit(app.exec_())
