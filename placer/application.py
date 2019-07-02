from os import listdir, rename
from os.path import isdir, isfile, join
from json import load, dump
from configparser import ConfigParser
from platform import system, release, python_version
from PyQt5.QtWidgets import (QMainWindow, QListWidgetItem, QMessageBox,
                             QFileDialog)
from PyQt5.QtCore import Qt, QEvent, QThread, pyqtSignal, pyqtSlot
from placer import __basedir__, __version__
from placer.ui.mainwindow import Ui_MainWindow
from placer.settings import SettingsDialog
from placer.edit import EditModDialog
from placer.save import SaveWorker
from placer.update import UpdateWorker
from placer.install import InstallWorker, InstallerManualDialog


class ModPlacer(QMainWindow):
    installHelper = pyqtSignal(str, dict, dict)

    def __init__(self):
        super().__init__()
        self._initialized = False
        self._config = ConfigParser()
        self._config.read("placer.ini")
        self._config.setdefault("Placer", {})
        self._config.setdefault("Updates", {})
        self._config["Placer"].setdefault("config", "")
        self._config["Placer"].setdefault("saveOnExit", "True")
        self._config["Placer"].setdefault("refreshOnFocus", "True")
        self._config["Placer"].setdefault("prettyPrint", "False")
        self._config["Placer"].setdefault("emptyData", "True")
        self._config["Updates"].setdefault("nexusApi", "")

        # Init all threads the workers will use
        self._saver = None
        self._saverThread = QThread(self)
        self._saverThread.finished.connect(self.refreshMods)
        self._updater = None
        self._updaterThread = QThread(self)
        self._installer = None
        self._installerThread = QThread(self)

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
        self.Ui.actionInstallMod.setEnabled(False)
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

        self.setWindowTitle(config[:-5] + " - Mod Placer")
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

        if self._config["Updates"]["nexusApi"]:
            self.Ui.actionCheckForUpdates.setEnabled(True)
            self._headers = {"User-Agent": f"ModPlacer/{__version__} "
                             f"({system()} {release()}) "
                             f"Python/{python_version()}",
                             "apikey": self._config["Updates"]["nexusApi"]}
        else:
            self.Ui.actionCheckForUpdates.setEnabled(False)
            self._headers = {}

        self._initialized = True
        self.Ui.actionInstallMod.setEnabled(True)
        self.Ui.actionRefresh.setEnabled(True)
        self.Ui.actionCheckForUpdates.setEnabled(True)
        self.Ui.modListWidget.clear()
        self.Ui.loadListWidget.clear()
        self.refreshMods(save=False)

    @pyqtSlot(str, str)
    def displayError(self, title, content):
        QMessageBox.critical(self, title, content, QMessageBox.Ok)

    def installMod(self):
        if self._installerThread.isRunning():
            return

        filters = "Archives (*.zip *.rar *.7z)"
        filePath = QFileDialog.getOpenFileName(self, "Select Zip",
                                               "", filters)
        if filePath[0]:
            self._installer = InstallWorker(self._modConf, self._headers,
                                            filePath[0])
            self._installer.moveToThread(self._installerThread)
            self._installer.installError.connect(self.displayError)
            self._installer.installer.connect(self.installerUI)
            self._installer.installFinished.connect(self.installerFinish)
            self.installHelper.connect(self._installer.complete)
            self._installerThread.started.connect(self._installer.prepare)
            self._installerThread.start()

    @pyqtSlot(str, dict, int, dict)
    def installerUI(self, name, data, installer, files):
        if not installer:
            dialog = InstallerManualDialog(name, data, self._modConf, self)
        if dialog.exec_():
            name, data = dialog.getData()
        else:
            name = ""
        self.installHelper.emit(name, data, files)

    @pyqtSlot(str, dict)
    def installerFinish(self, name, data):
        if name:
            self._modDB[name] = data
            self.addModItem(name, data)
        self._installer = None
        self._installerThread.quit()

    def refreshMods(self, *, save=True):
        if ((isdir(self._modConf["data"]) and isdir(self._modConf["mods"])) or
                not self._installerThread.isRunning() or
                not self._saverThread.isRunning()):
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
                data = {"version": "1.0", "id": ""}
            item = self.createItem(name, check=check, data=data)
            self.Ui.modListWidget.addItem(item)

    def addLoadItem(self, name, check=Qt.Unchecked):
        if (name.lower().endswith((".esm", ".esp", ".esl")) and
                isfile(join(self._modConf["data"], name)) and
                not self.Ui.loadListWidget.findItems(name, Qt.MatchExactly)):
            index = self.Ui.loadListWidget.count()
            data = {"index": index, "id": f"{index:02X}"}
            item = self.createItem(name, check=check, data=data)
            self.Ui.loadListWidget.addItem(item)

    def changeModInfo(self, item):
        dialog = EditModDialog(item, self._modConf, self)
        if dialog.exec_():
            oldName = item.data(Qt.UserRole)
            item = dialog.getItem()
            if oldName != item.data(Qt.UserRole):
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

        self._saver = SaveWorker(self._config, self._modConf, mods, plugins)
        self._saver.moveToThread(self._saverThread)
        self._saver.finished.connect(self._saverThread.quit)
        self._saverThread.started.connect(self._saver.save)
        self._saverThread.start()

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

        with open(join(__basedir__, self._config["Placer"]["config"]),
                  "w") as f:
            if self._config["Placer"].getboolean("prettyPrint"):
                dump(self._modConf, f, indent=4)
            else:
                dump(self._modConf, f, separators=(",", ":"))

        with open(join(self._modConf["mods"], "database.json"), "w") as f:
            if self._config["Placer"].getboolean("prettyPrint"):
                dump(self._modDB, f, indent=4)
            else:
                dump(self._modDB, f, separators=(",", ":"))

        with open(join(__basedir__, "placer.ini"), "w") as f:
            self._config.write(f)

    def checkUpdates(self):
        self.Ui.actionCheckForUpdates.setEnabled(False)
        mods = []
        for index in range(self.Ui.modListWidget.count()):
            mod = self.Ui.modListWidget.item(index)
            mods.append(mod)

        self._updater = UpdateWorker(mods, self._modConf["game"],
                                     self._headers)
        self._updater.moveToThread(self._updaterThread)
        self._updater.finished.connect(self.finishUpdate)
        self._updaterThread.started.connect(self._updater.fetchUpdates)
        self._updaterThread.start()

    @pyqtSlot(str)
    def finishUpdate(self, updates):
        self.Ui.actionCheckForUpdates.setEnabled(True)
        QMessageBox.information(self, "Mod updates", updates, QMessageBox.Ok)
        self._updaterThread.quit()

    def closeEvent(self, event):
        if (self._saverThread.isRunning() or
                self._updaterThread.isRunning() or
                self._installerThread.isRunning()):
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
