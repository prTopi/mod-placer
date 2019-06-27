from os import listdir, unlink
from json import load, dump
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from placer.ui.config import Ui_ConfigDialog
from placer.edit import EditConfigDialog


class SettingsDialog(QDialog):
    def __init__(self, config, parent):
        super().__init__(parent)
        self._config = config
        self.Ui = Ui_ConfigDialog()
        self.Ui.setupUi(self)
        self.Ui.apiLineEdit.setText(self._config["Nexus"]["api"])
        self.Ui.configComboBox.currentTextChanged.connect(self.update)
        self.Ui.editPushButton.clicked.connect(lambda: self.editConfig(
            name=self.Ui.configComboBox.currentText()))
        self.Ui.addToolButton.clicked.connect(self.editConfig)
        self.Ui.exitCheckBox.setChecked(
            self._config["Placer"].getboolean("saveOnExit"))
        self.Ui.focusCheckBox.setChecked(
            self._config["Placer"].getboolean("refreshOnFocus"))
        self.Ui.prettyCheckBox.setChecked(
            self._config["Placer"].getboolean("prettyPrint"))
        self.refresh(self._config["Placer"]["config"])
        self.show()

    def refresh(self, config):
        self.Ui.configComboBox.clear()
        for file in listdir():
            if file.endswith(".json"):
                self.Ui.configComboBox.addItem(file)
        if config:
            if self.Ui.configComboBox.findText(config, Qt.MatchExactly) != -1:
                self.Ui.configComboBox.setCurrentIndex(
                    self.Ui.configComboBox.findText(config, Qt.MatchExactly))
            else:
                self.Ui.configComboBox.setCurrentIndex(0)

    def editConfig(self, *, name=""):
        if name in listdir():
            with open(name) as f:
                config = load(f)
        else:
            config = {}
        if name.endswith(".json"):
            name = name[:-5]
        config.setdefault("game", "")
        config.setdefault("data", "")
        config.setdefault("mods", "")
        config.setdefault("plugins", "")
        config.setdefault("prefix", "")
        config.setdefault("ModOrder", {})
        config.setdefault("LoadOrder", {})
        dialog = ConfigEditDialog(name, config, self)
        if dialog.exec_():
            oldName = name + ".json"
            name, config = dialog.getConfig()
            if not name.endswith(".json"):
                name = name + ".json"
            with open(name, "w") as f:
                dump(config, f)
            if oldName != name:
                if oldName in listdir():
                    unlink(oldName)
        self.refresh(name)

    def update(self, text):
        if text:
            self.Ui.buttonBox.setEnabled(True)
        else:
            self.Ui.buttonBox.setEnabled(False)

    def getConfig(self):
        self._config["Placer"]["config"] = self.Ui.configComboBox.currentText()
        self._config["Placer"]["saveOnExit"] = str(bool(
            self.Ui.exitCheckBox.isChecked()))
        self._config["Placer"]["refreshOnFocus"] = str(bool(
            self.Ui.focusCheckBox.isChecked()))
        self._config["Placer"]["prettyPrint"] = str(bool(
            self.Ui.prettyCheckBox.isChecked()))
        self._config["Nexus"]["api"] = self.Ui.apiLineEdit.text()
        return self._config
