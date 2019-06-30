from os import listdir, rename, utime
from os.path import isdir, isfile, join
from json import load, dump
from configparser import ConfigParser
from platform import system, release, python_version
from PyQt5.QtWidgets import (QMainWindow, QListWidgetItem, QMessageBox,
                             QFileDialog)
from PyQt5.QtCore import Qt, QEvent, QThread, pyqtSlot
from placer import __version__
from placer.ui.mainwindow import Ui_MainWindow
from placer.settings import SettingsDialog
from placer.edit import EditModDialog
from placer.save import SaveThread
from placer.update import UpdateThread
from placer.install import InstallThread


class ModPlacer(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initialized = False
        self._config = ConfigParser()
        self._config.read("placer.ini")
        self._config.setdefault("Placer", {})
        self._config.setdefault("Nexus", {})
        self._config["Placer"].setdefault("config", "")
        self._config["Placer"].setdefault("saveOnExit", True)
        self._config["Placer"].setdefault("refreshOnFocus", True)
        self._config["Placer"].setdefault("prettyPrint", False)
        self._config["Nexus"].setdefault("api", "")
        # Create blank QThreads so that we can use self._thread.isRunning()
        self._saver = QThread()
        self._updater = QThread()
        self._installer = QThread()
        # UI is located in a different file, created with QtDesigner
        self.Ui = Ui_MainWindow()
        self.Ui.setupUi(self)
        self.Ui.actionSeparator.setSeparator(True)
        self.Ui.actionInstallMod.triggered.connect(self.installMod)
        self.Ui.actionEditMod.triggered.connect(lambda: self.changeModInfo(
            self.Ui.modListWidget.currentItem()))
        self.Ui.actionRefresh.triggered.connect(self.refreshMods)
        self.Ui.actionCheckForUpdates.triggered.connect(self.checkUpdates)
        self.Ui.actionSettings.triggered.connect(self.loadConfig)
        self.Ui.modListWidget.itemDoubleClicked.connect(self.changeModInfo)
        self.Ui.modListWidget.addAction(self.Ui.actionInstallMod)
        self.Ui.modListWidget.addAction(self.Ui.actionEditMod)
        self.Ui.modListWidget.addAction(self.Ui.actionRefresh)
        self.Ui.modListWidget.addAction(self.Ui.actionSeparator)
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
        try:
            with open(join(self._modConf["mods"], "database.json")) as f:
                self._modDB = load(f)
        except FileNotFoundError:
            self._modDB = {}
        self._data = self._modConf.get("data", "Data")
        self._mods = self._modConf.get("mods", "mods")
        self.setWindowTitle(config[:-5] + " - Mod Placer")
        if self._config["Nexus"]["api"]:
            self.Ui.actionCheckForUpdates.setEnabled(True)
            self._headers = {"User-Agent": f"ModPlacer/{__version__} "
                            f"({system()} {release()}) "
                            f"Python/{python_version()}",
                            "apikey": self._config["Nexus"]["api"]}
        else:
            self.Ui.actionCheckForUpdates.setEnabled(False)
            self._headers = {}
        self._initialized = True
        self.Ui.actionRefresh.setEnabled(True)
        self.Ui.actionCheckForUpdates.setEnabled(True)
        self.Ui.modListWidget.clear()
        self.Ui.loadListWidget.clear()
        self.refreshMods(save=False)

    @pyqtSlot(str, str)
    def displayError(self, title, content):
        QMessageBox.critical(self, title, content, QMessageBox.Ok)

    def installMod(self):
        if self._installer.isRunning():
            return
        filters = "Archives (*.zip *.rar *.7z)"
        filePath = QFileDialog.getOpenFileName(self, "Select Zip",
                                               "", filters)
        if filePath[0]:
            self._installer = InstallThread(self._modConf, self._headers,
                                            filePath[0], self)
            self._installer.installError.connect(self.displayError)
            self._installer.finishInstall.connect(self.installFinish)
            self._installer.start()

    @pyqtSlot(str, dict)
    def installFinish(self, name, data):
        if len(name):
            found = self.Ui.modListWidget.findItems(name, Qt.MatchExactly)
            if found:
                item = found[0]
            else:
                item = self.createItem(name, Qt.Unchecked, data=data)
                self.Ui.modListWidget.addItem(item)
            self.changeModInfo(item)

    def refreshMods(self, *, save=True):
        if isdir(self._modConf["data"]) and isdir(self._modConf["mods"]):
            self.Ui.savePushButton.setEnabled(True)
        else:
            self.Ui.savePushButton.setEnabled(False)
            return
        if save:
            self.saveConfig()
        self.Ui.modListWidget.clear()
        for index in self._modConf["ModOrder"]:
            self.addModItem(*self._modConf["ModOrder"][index])
        for folder in listdir(self._modConf["mods"]):
            self.addModItem(folder)
        self.Ui.loadListWidget.clear()
        for plugin in self._modConf["LoadOrder"]:
            self.addLoadItem(*self._modConf["LoadOrder"][plugin])
        for plugin in listdir(self._modConf["data"]):
                self.addLoadItem(plugin)

    def createItem(self, name, check, data={}):
        item = QListWidgetItem(name)
        item.setData(Qt.CheckStateRole, check)
        item.setData(Qt.UserRole, name)
        for index, x in enumerate(data):
            item.setData(Qt.UserRole + index + 1, data[x])
        tooltip = "\n".join([f"{x.title()}: {data[x]}" for x in data])
        item.setToolTip(tooltip)
        return item

    def addModItem(self, name, check=Qt.Unchecked):
        if (isdir(join(self._modConf["mods"], name)) and
                not self.Ui.modListWidget.findItems(name, Qt.MatchExactly)):
            try:
                data = self._modDB[name]
            except KeyError:
                data={"version": "1.0", "id": ""}
            item = self.createItem(name, check=check, data=data)
            self.Ui.modListWidget.addItem(item)

    def addLoadItem(self, name, check=Qt.Unchecked):
        if (name.lower().endswith((".esm", ".esp", ".esl")) and
                isfile(join(self._modConf["data"], name)) and
                not self.Ui.loadListWidget.findItems(name, Qt.MatchExactly)):
            index = self.Ui.loadListWidget.count()
            data={"index": index, "id": f"{index:02X}"}
            item = self.createItem(name, check=check, data=data)
            self.Ui.loadListWidget.addItem(item)

    def changeModInfo(self, item):
        self.dialog = EditModDialog(item, self._modConf["game"], self)
        if self.dialog.exec_():
            oldName = item.data(Qt.UserRole)
            item = self.dialog.getItem()
            if oldName != item.data(Qt.UserRole):
                if item.data(Qt.UserRole) in listdir(self._modConf["mods"]):
                    QMessageBox.warning(self, "Warning", "Mod with that name "
                                        "already exists.", QMessageBox.Ok)
                else:
                    rename(join(self._modConf["mods"], oldName),
                           join(self._modConf["mods"], item.data(Qt.UserRole)))
                    item.setText(item.data(Qt.UserRole))
            item.setToolTip(f"Version: {item.data(Qt.UserRole + 1)}\n"
                            f"Id: {item.data(Qt.UserRole + 2)}")

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
        plugins = {}
        for index in range(self.Ui.loadListWidget.count()):
            plugin = self.Ui.loadListWidget.item(index)
            plugins[plugin.data(Qt.UserRole)] = plugin.checkState()
        self._saver = SaveThread(self._modConf, mods, plugins, self)
        self._saver.finished.connect(self.refreshMods)
        self._saver.start()

    def saveConfig(self):
        if (not isdir(self._modConf["data"]) and
                not isdir(self._modConf["mods"])):
            return
        self._modConf["ModOrder"] = {}
        self._modDB = {}
        for index in range(self.Ui.modListWidget.count()):
            mod = self.Ui.modListWidget.item(index)
            name = mod.data(Qt.UserRole)
            self._modConf["ModOrder"][index] = (name,
                                                mod.checkState())
            self._modDB[name] = {"version": mod.data(Qt.UserRole + 1),
                                 "id": mod.data(Qt.UserRole + 2)}
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
        with open(join(self._modConf["mods"], "database.json"), "w") as f:
            if self._config["Placer"].getboolean("prettyPrint"):
                dump(self._modDB, f, indent=4)
            else:
                dump(self._modDB, f, separators=(",", ":"))
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
        if (self._saver.isRunning() or self._updater.isRunning() or
                self._installer.isRunning()):
            msg = "Worker thread(s) are currently running.\n" \
                "Are you sure you want to exit?"
            dial = QMessageBox.question(self, "Are you sure?", msg,
                                        QMessageBox.Yes | QMessageBox.No)
            if dial == QMessageBox.No:
                event.ignore()
                return
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
