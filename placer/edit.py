from os import listdir
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
from placer.ui.editconfig import Ui_EditConfigDialog
from placer.ui.editmod import Ui_EditModDialog


class EditConfigDialog(QDialog):
    def __init__(self, name, config, parent):
        super().__init__(parent)
        self._name = name
        self._config = config
        self.Ui = Ui_EditConfigDialog()
        self.Ui.setupUi(self)
        self.Ui.nameLineEdit.setText(name)
        self.Ui.gameLineEdit.setText(config["game"])
        self.Ui.dataLineEdit.setText(config["data"])
        self.Ui.dataToolButton.clicked.connect(lambda: self.browseDirectory(
            self.Ui.dataLineEdit))
        self.Ui.modsLineEdit.setText(config["mods"])
        self.Ui.modsToolButton.clicked.connect(lambda: self.browseDirectory(
            self.Ui.modsLineEdit))
        self.Ui.pluginsLineEdit.setText(config["plugins"])
        self.Ui.pluginsToolButton.clicked.connect(lambda: self.browseFile(
            self.Ui.pluginsLineEdit))
        self.Ui.prefixLineEdit.setText(config["prefix"])
        self.show()

    def browseDirectory(self, lineEdit):
        dirPath = QFileDialog.getExistingDirectory(self, "Select Folder",
                                                   lineEdit.text())
        if dirPath:
            lineEdit.setText(dirPath)

    def browseFile(self, lineEdit):
        filePath = QFileDialog.getOpenFileName(self, "Select File",
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
        self._config["game"] = self.Ui.gameLineEdit.text()
        self._config["data"] = self.Ui.dataLineEdit.text()
        self._config["mods"] = self.Ui.modsLineEdit.text()
        self._config["plugins"] = self.Ui.pluginsLineEdit.text()
        self._config["prefix"] = self.Ui.prefixLineEdit.text()
        return self.Ui.nameLineEdit.text(), self._config


class EditModDialog(QDialog):
    def __init__(self, item, game, parent):
        super().__init__(parent)
        self._item = item
        self.Ui = Ui_EditModDialog()
        self.Ui.setupUi(self)
        self.Ui.nameLineEdit.setText(item.data(Qt.UserRole))
        self.Ui.versionLineEdit.setText(item.data(Qt.UserRole + 1))
        nexusInfo = item.data(Qt.UserRole + 2).split("|")
        self.Ui.idLineEdit.setText(nexusInfo[0])
        if len(nexusInfo) != 1:
            self.Ui.gameLineEdit.setText(nexusInfo[1])
        self.Ui.gameLineEdit.setPlaceholderText(game)
        self.show()

    def getItem(self):
        self._item.setData(Qt.UserRole, self.Ui.nameLineEdit.text())
        self._item.setData(Qt.UserRole + 1, self.Ui.versionLineEdit.text())
        nexusInfo = self.Ui.idLineEdit.text()
        game = self.Ui.gameLineEdit.text()
        if game:
            nexusInfo = f"{nexusInfo}|{game}"
        self._item.setData(Qt.UserRole + 2, nexusInfo)
        return self._item
