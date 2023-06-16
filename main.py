import sys

from modules import Parser, QApplication, MainWindow, FileWorker


if __name__ == '__main__':
    parser = Parser()
    app = QApplication([])
    parser_app = MainWindow(FileWorker, parser)
    parser_app.show()
    sys.exit(app.exec_())
