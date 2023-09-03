# /* coding: UTF-8 */

from os import path
from PyQt5.QtGui import QIcon


def icon(name):
    """Создаёт иконку, которую можно положить на виджеты или главное окно."""

    folder_path = path.join(path.dirname(__file__))
    return QIcon(path.join(folder_path, name))
