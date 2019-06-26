from os import listdir
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QVBoxLayout,
                             QLineEdit, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from placer.ui.editconfig import Ui_ConfigEditDialog


class ConfigEditDialog(QDialog):
    def __init__(self, name, config, parent):
        super().__init__(parent)
        self._name = name
        self._config = config
        self.Ui = Ui_ConfigEditDialog()
        self.Ui.setupUi(self)
        self.Ui.nameLineEdit.setText(name)
        self.Ui.gameLineEdit.setText(config["Settings"]["game"])
        self.Ui.dataLineEdit.setText(config["Settings"]["data"])
        self.Ui.dataToolButton.clicked.connect(lambda: self.browseDirectory(
            self.Ui.dataLineEdit))
        self.Ui.modsLineEdit.setText(config["Settings"]["mods"])
        self.Ui.modsToolButton.clicked.connect(lambda: self.browseDirectory(
            self.Ui.modsLineEdit))
        self.Ui.pluginsLineEdit.setText(config["Settings"]["plugins"])
        self.Ui.pluginsToolButton.clicked.connect(lambda: self.browseFile(
            self.Ui.pluginsLineEdit))
        self.Ui.prefixLineEdit.setText(config["Settings"]["pluginpref"])
        self.show()

    def browseDirectory(self, lineEdit):
        dirPath = QFileDialog.getExistingDirectory(self, 'Select Folder',
                                                   lineEdit.text())
        if dirPath:
            lineEdit.setText(dirPath)

    def browseFile(self, lineEdit):
        filePath = QFileDialog.getOpenFileName(self, 'Select File',
                                                   lineEdit.text())
        if filePath[0]:
            lineEdit.setText(filePath[0])

    def accept(self):
        name = self.Ui.nameLineEdit.text()
        if name != self._name and name + ".json" in listdir():
            QMessageBox.warning(self, "File already exists",
                                "Mod config with that name already exists.",
                                QMessageBox.Ok)
            return
        super().accept()

    def getConfig(self):
        self._config["Settings"]["game"] = self.Ui.gameLineEdit.text()
        self._config["Settings"]["data"] = self.Ui.dataLineEdit.text()
        self._config["Settings"]["mods"] = self.Ui.modsLineEdit.text()
        self._config["Settings"]["plugins"] = self.Ui.pluginsLineEdit.text()
        self._config["Settings"]["pluginpref"] = self.Ui.prefixLineEdit.text()
        return self.Ui.nameLineEdit.text(), self._config


class EditDialog(QDialog):
    def __init__(self, editBoxes, parent):
        super().__init__(parent)
        self.setWindowTitle("Edit - Mod Placer")
        self.setModal(True)
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
