import sys

import page_parser
import worker
import interface

if __name__ == '__main__':
    parser = page_parser.Parser()
    app = interface.QApplication([])
    parser_app = interface.ParserInterface(worker.FileWorker, parser)
    parser_app.show()
    sys.exit(app.exec_())
