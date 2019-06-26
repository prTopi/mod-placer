#!/usr/bin/env python3
from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from placer.application import ModPlacer


if __name__ == "__main__":
    app = QApplication(argv)
    window = ModPlacer()
    exit(app.exec_())
