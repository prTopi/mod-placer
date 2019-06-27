from os import listdir, path, rename, utime
from json import load, dump
from configparser import ConfigParser
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt, QEvent, pyqtSlot
from placer.ui.mainwindow import Ui_MainWindow
from placer.settings import SettingsDialog
from placer.edit import EditModDialog
from placer.save import SaveThread
from placer.update import UpdateThread


class ModPlacer(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initialized = False
        self._config = ConfigParser()
        if not self._config.read("placer.ini"):
            self._config["Placer"] = {"config": "", "saveOnExit": True,
                                      "refreshOnFocus": True,
                                      "prettyPrint": False}
            self._config["Nexus"] = {"api": ""}
        self._saver = None
        self._updater = None
        self.Ui = Ui_MainWindow()
        self.Ui.setupUi(self)
        self.Ui.actionRefresh.triggered.connect(self.refreshMods)
        self.Ui.actionCheckForUpdates.triggered.connect(self.checkUpdates)
        self.Ui.actionSettings.triggered.connect(self.loadConfig)
        self.Ui.modListWidget.itemDoubleClicked.connect(self.changeModInfo)
        self.Ui.modListWidget.addAction(self.Ui.actionRefresh)
        self.Ui.modListWidget.addAction(self.Ui.actionCheckForUpdates)
        self.Ui.savePushButton.clicked.connect(self.saveMods)
        self.show()
        self.loadConfig(config=self._config["Placer"]["config"])

    def loadConfig(self, *, config=""):
        self._initialized = False
        self.Ui.savePushButton.setEnabled(False)
        self.Ui.actionRefresh.setEnabled(False)
        self.Ui.actionCheckForUpdates.setEnabled(False)
        if config == "":
            dialog = SettingsDialog(self._config, self)
            if dialog.exec_():
                self._config = dialog.getConfig()
            else:
                return
        config = self._config["Placer"]["config"]
        try:
            with open(self._config["Placer"]["config"]) as f:
                self._modConf = load(f)
        except FileNotFoundError:
            self.loadConfig()
            return
        self._modConf.setdefault("game", config[:-5])
        self._modConf.setdefault("data", "Data")
        self._modConf.setdefault("mods", "mods")
        self._modConf.setdefault("plugins", "")
        self._modConf.setdefault("prefix", "")
        self._modConf.setdefault("ModOrder", {})
        self._modConf.setdefault("LoadOrder", {})
        self._data = self._modConf.get("data", "Data")
        self._mods = self._modConf.get("mods", "mods")
        self.setWindowTitle(config[:-5] + " - Mod Placer")
        if self._config["Nexus"]["api"]:
            self.Ui.actionCheckForUpdates.setEnabled(True)
        else:
            self.Ui.actionCheckForUpdates.setEnabled(False)
        self._initialized = True
        self.Ui.actionRefresh.setEnabled(True)
        self.Ui.actionCheckForUpdates.setEnabled(True)
        self.Ui.modListWidget.clear()
        self.Ui.loadListWidget.clear()
        self.refreshMods(save=False)

    def refreshMods(self, *, save=True):
        if path.isdir(self._data) and path.isdir(self._mods):
            self.Ui.savePushButton.setEnabled(True)
        else:
            self.Ui.savePushButton.setEnabled(False)
            return
        if save:
            self.saveConfig()
        self.Ui.modListWidget.clear()
        for mod in self._modConf["ModOrder"]:
            self.addModItem(*self._modConf["ModOrder"][mod])
        for mod in listdir(self._mods):
            self.addModItem(mod)
        self.Ui.loadListWidget.clear()
        for plugin in self._modConf["LoadOrder"]:
            self.addLoadItem(*self._modConf["LoadOrder"][plugin])
        for plugin in listdir(self._data):
            if plugin.endswith((".esm", ".esp", ".esl")):
                self.addLoadItem(plugin)

    def changeModInfo(self, item):
        self.dialog = EditModDialog(item, self._modConf["game"], self)
        if self.dialog.exec_():
            oldName = item.data(Qt.UserRole)
            item = self.dialog.getItem()
            if oldName != item.data(Qt.UserRole):
                if item.data(Qt.UserRole) in listdir(self._mods):
                    QMessageBox.warning(self, "Warning", "Mod with that name "
                                        "already exists.", QMessageBox.Ok)
                else:
                    rename(path.join(self._mods, oldName),
                           path.join(self._mods, item.data(Qt.UserRole)))
                    item.setText(item.data(Qt.UserRole))
            item.setToolTip(f"Version: {item.data(Qt.UserRole + 1)}\n"
                            f"ID: {item.data(Qt.UserRole + 2)}")

    def addModItem(self, name, check=Qt.Unchecked, version="1.0", modID=""):
        if path.isdir(path.join(self._mods, name)):
            if not self.Ui.modListWidget.findItems(name, Qt.MatchExactly):
                item = QListWidgetItem(name)
                item.setData(Qt.CheckStateRole, check)
                item.setData(Qt.UserRole, name)
                item.setData(Qt.UserRole + 1, version)
                item.setData(Qt.UserRole + 2, modID)
                item.setToolTip(f"Version: {version}\nID: {modID}")
                self.Ui.modListWidget.addItem(item)

    def addLoadItem(self, name, check=Qt.Unchecked):
        if path.islink(path.join(self._data, name)):
            if not self.Ui.loadListWidget.findItems(name, Qt.MatchExactly):
                item = QListWidgetItem(name)
                item.setData(Qt.CheckStateRole, check)
                item.setData(Qt.UserRole, name)
                index = self.Ui.loadListWidget.count()
                item.setToolTip(f"Index: {index}\nHex: {index:02X}")
                self.Ui.loadListWidget.addItem(item)

    def saveMods(self):
        self.refreshMods()
        if not self.Ui.savePushButton.isEnabled():
            return
        self.Ui.savePushButton.setEnabled(False)
        mods = []
        for index in range(self.Ui.modListWidget.count()):
            mod = self.Ui.modListWidget.item(index)
            if mod.checkState():
                mods.append(mod.data(Qt.UserRole))
        plugins = []
        for index in range(self.Ui.loadListWidget.count()):
            plugin = self.Ui.loadListWidget.item(index)
            if plugin.checkState():
                plugins.append(plugin.data(Qt.UserRole))
        self._saver = SaveThread(self._modConf, mods,
                                      plugins, self)
        self._saver.finished.connect(self.refreshMods)
        self._saver.start()

    def saveConfig(self):
        if not path.isdir(self._data) and not path.isdir(self._mods):
            return
        self._modConf["ModOrder"] = {}
        for index in range(self.Ui.modListWidget.count()):
            mod = self.Ui.modListWidget.item(index)
            self._modConf["ModOrder"][index] = (mod.data(Qt.UserRole),
                                              mod.checkState(),
                                              mod.data(Qt.UserRole + 1),
                                              mod.data(Qt.UserRole + 2))
        self._modConf["LoadOrder"] = {}
        for index in range(self.Ui.loadListWidget.count()):
            plugin = self.Ui.loadListWidget.item(index)
            self._modConf["LoadOrder"][index] = [plugin.data(Qt.UserRole),
                                              plugin.checkState()]
        with open(self._config["Placer"]["config"], "w") as f:
            if self._config["Placer"].getboolean("prettyPrint"):
                dump(self._modConf, f, indent=4)
            else:
                dump(self._modConf, f, separators=(",", ":"))
        with open("placer.ini", "w") as f:
            self._config.write(f)

    def checkUpdates(self):
        self.Ui.actionCheckForUpdates.setEnabled(False)
        mods = []
        for index in range(self.Ui.modListWidget.count()):
            mod = self.Ui.modListWidget.item(index)
            mods.append(mod)
        self._updater = UpdateThread(mods, self._modConf["game"],
                                     self._config["Nexus"]["api"], self)
        self._updater.signalFinished.connect(self.finishUpdate)
        self._updater.start()

    @pyqtSlot(str)
    def finishUpdate(self, updates):
        self.Ui.actionCheckForUpdates.setEnabled(True)
        QMessageBox.information(self, "Mod updates", updates, QMessageBox.Ok)

    def closeEvent(self, event):
        if (self._config["Placer"].getboolean("saveOnExit") and
                self._initialized):
            self.saveConfig()
        super().closeEvent(event)

    def event(self, event):
        if event.type() == QEvent.ActivationChange:
            if (self.isActiveWindow() and
                    self._config["Placer"].getboolean("refreshOnFocus") and
                    self._initialized):
                self.refreshMods()
        return super().event(event)
