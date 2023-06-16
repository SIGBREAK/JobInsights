import sys
import traceback

from PyQt5.QtWidgets import (QApplication, QMessageBox)
from .page_parser import Parser
from .worker import FileWorker
from .interface import MainWindow


def log_uncaught_exceptions(ex_cls, ex, tb):
    """Функция, которая позволяет выводить (в консоль и отдельне окно) ошибки интерфейса, идущие мимо stderr"""
    text = f'{ex_cls.__name__}: {ex}:\n'
    text += ''.join(traceback.format_tb(tb))
    print(text)
    QMessageBox.critical(None, 'Ошибка!', text)
    sys.exit()


sys.excepthook = log_uncaught_exceptions


