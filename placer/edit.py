from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLabel,
                             QVBoxLayout, QLineEdit)
from PyQt5.QtCore import Qt


class EditDialog(QDialog):
    def __init__(self, editBoxes, parent):
        super().__init__(parent)
        self.setWindowTitle('Edit - Mod Placer')
        layout = QVBoxLayout(self)
        for box in editBoxes:
            layout.addWidget(QLabel(box, self))
            layout.addWidget(QLineEdit(editBoxes[box], self))
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setMinimumWidth(400)
        self.show()

    def getValues(self):
        return [box.text() for box in self.findChildren(QLineEdit)]
