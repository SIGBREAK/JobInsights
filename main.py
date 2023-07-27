import sys

from PyQt5.QtWidgets import QApplication
from modules import MainWindow


if __name__ == '__main__':
    app = QApplication([])
    parser_app = MainWindow()
    parser_app.show()
    sys.exit(app.exec_())
