# /* coding: UTF-8 */

import sys
import traceback

from PyQt5.QtWidgets import QMessageBox
from .user_interface import MainWindow


def log_uncaught_exceptions(ex_cls, ex, tb):
    """Функция, которая позволяет выводить (в консоль и отдельное окно) ошибки интерфейса, идущие мимо stderr"""

    text = f'{ex_cls.__name__}: {ex}:\n'
    text += ''.join(traceback.format_tb(tb))
    print(text)
    QMessageBox.critical(None, 'Ошибка!', text)
    sys.exit()


sys.except_hook = log_uncaught_exceptions
