# /* coding: UTF-8 */

import sys

from PyQt5.QtWidgets import QApplication
from modules import MainWindow


def main():
    """Запуск главного окна парсера JobInsights."""
    app = QApplication([])
    parser_app = MainWindow()
    parser_app.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
