from os import listdir
from json import load, dump
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt
from placer.ui.options import Ui_ConfigDialog
from placer.edit import EditDialog


class OptionsDialog(QDialog):
    def __init__(self, config, api, parent):
        super().__init__(parent)
        self.Ui = Ui_ConfigDialog()
        self.Ui.setupUi(self)
        self.Ui.lineEditApi.setText(api)
        self.Ui.comboBoxConfig.currentTextChanged.connect(self.update)
        self.Ui.pushButtonEdit.clicked.connect(lambda: self.editConfig(
            self.Ui.comboBoxConfig.currentText()))
        self.Ui.toolButtonAdd.clicked.connect(lambda: self.editConfig(''))
        self.Ui.buttonBox.accepted.connect(self.accept)
        self.Ui.buttonBox.rejected.connect(self.reject)
        self.refresh(config)
        self.show()

    def refresh(self, config):
        self.Ui.comboBoxConfig.clear()
        for file in listdir():
            if file.endswith(".json"):
                self.Ui.comboBoxConfig.addItem(file[:-5])
        if config:
            if self.Ui.comboBoxConfig.findText(config, Qt.MatchExactly) != -1:
                self.Ui.comboBoxConfig.setCurrentIndex(
                    self.Ui.comboBoxConfig.findText(config, Qt.MatchExactly))
            else:
                self.Ui.comboBoxConfig.setCurrentIndex(0)

    def editConfig(self, name):
        self.setEnabled(False)
        if name + ".json" in listdir():
            with open(name + ".json") as f:
                config = load(f)
        else:
            config = {"Settings": {}, "Mods": {}, "Load": {}}
        game = config["Settings"].get("game", "")
        mods = config["Settings"].get("mods", "")
        data = config["Settings"].get("data", "")
        plugins = config["Settings"].get("plugins", "")
        prefix = config["Settings"].get("pluginpref", "")
        dialog = EditDialog({"File Name": name, "Nexus Game": game,
                             "Mods Directory": mods, "Data Path": data,
                             "Plugins.txt File": plugins,
                             "Plugins.txt Line Prefix": prefix}, self)
        if dialog.exec_():
            name, game, mods, data, plugins, prefix = dialog.getValues()
            if (self.Ui.comboBoxConfig.currentText() != name and
                    name + ".json" in listdir()):
                QMessageBox.warning(self, "File already exists",
                                    "Mod config with that name already "
                                    "exists.", QMessageBox.Ok)
                name = self.Ui.comboBoxConfig.currentText()
            config["Settings"] = {"data": data, "game": game, "mods": mods,
                                  "plugins": plugins, "pluginpref": prefix}
            config.setdefault("Mods", {})
            config.setdefault("Load", {})
            with open(name + ".json", "w") as f:
                dump(config, f)
        self.refresh(name)
        self.setEnabled(True)

    def update(self, text):
        if text:
            self.Ui.buttonBox.setEnabled(True)
        else:
            self.Ui.buttonBox.setEnabled(False)

    def getValues(self):
        return self.Ui.lineEditApi.text(), self.Ui.comboBoxConfig.currentText()
