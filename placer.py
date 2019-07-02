#!/usr/bin/env python3
from sys import argv, exit, version_info
from PyQt5.QtWidgets import QApplication, QMessageBox
from placer.application import ModPlacer


if __name__ == "__main__":
    app = QApplication(argv)
    if version_info >= (3, 6):
        window = ModPlacer()
        exit(app.exec_())
    else:
        QMessageBox.critical(None, "Python update needed",
                             "Only Python versions above 3.6 are supported.\n"
                             "Please update your Python version.",
                             QMessageBox.Close)
