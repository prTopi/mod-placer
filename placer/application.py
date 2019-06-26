#!/usr/bin/env python3
from sys import argv, exit
from platform import system, release, python_version
from os import (listdir, path, rename, symlink, makedirs, rmdir,
                unlink, utime)
from shutil import copy2
from json import load, dump
from urllib.request import urlopen, Request
from configparser import ConfigParser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidgetItem,
                             QMessageBox)
from PyQt5.QtCore import Qt, QEvent, QThread, pyqtSlot
from placer.ui.mainwindow import Ui_MainWindow
from placer.options import OptionsDialog
from placer.edit import EditDialog
from placer.commit import CommitThread

__version__ = "0.2.7"


class ModPlacer(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initialized = False
        self._config = ConfigParser()
        if not self._config.read("placer.ini"):
            self._config["Placer"] = {"config": "", "saveOnExit": True,
                                      "refreshOnFocus": True}
            self._config["Nexus"] = {"api": ""}
        self._commiter = None
        self.Ui = Ui_MainWindow()
        self.Ui.setupUi(self)
        self.Ui.modListWidget.itemDoubleClicked.connect(self.changeModInfo)
        self.Ui.commitPushButton.clicked.connect(self.selectCommit)
        self.Ui.actionRefresh.triggered.connect(self.refreshMods)
        self.Ui.actionCheckForUpdates.triggered.connect(self.checkUpdates)
        self.Ui.actionOptions.triggered.connect(self.loadConfig)
        self.Ui.actionQuit.triggered.connect(self.close)
        self.show()
        self.loadConfig(config=self._config["Placer"]["config"])

    def loadConfig(self, *, config=""):
        self._initialized = False
        self.Ui.commitPushButton.setEnabled(False)
        self.Ui.actionRefresh.setEnabled(False)
        self.Ui.actionCheckForUpdates.setEnabled(False)
        if config == "":
            dialog = OptionsDialog(self._config, self)
            if dialog.exec_():
                self._config = dialog.getConfig()
            else:
                return
        config = self._config["Placer"]["config"]
        try:
            with open(config) as f:
                self._modConfig = load(f)
        except FileNotFoundError:
            self.loadConfig()
            return
        self._modConfig.setdefault("Settings", {})
        self._modConfig.setdefault("Mods", {})
        self._modConfig.setdefault("Load", {})
        self._game = self._modConfig["Settings"].get("game", config[:-5])
        self._data = self._modConfig["Settings"].get("data", "Data")
        self._mods = self._modConfig["Settings"].get("mods", "mods")
        self._plugins = self._modConfig["Settings"].get("plugins", "")
        self._pluginPrefix = self._modConfig["Settings"].get("pluginpref", "")
        self.setWindowTitle(config[:-5] + " - Mod Placer")
        if self._config["Nexus"]["api"]:
            self.Ui.actionCheckForUpdates.setEnabled(True)
            self._headers = {"User-Agent": f"ModPlacer/{__version__} "
                             f"({system()} {release()}) "
                             f"Python/{python_version()}",
                             "apikey": self._config["Nexus"]["api"]}
        else:
            self.Ui.actionCheckForUpdates.setEnabled(False)
        if self._plugins != "":
            if not path.isdir(path.dirname(self._plugins)):
                QMessageBox.critical(self, "Error", "Plugins folder not found."
                                     f" ({path.dirname(self._plugins)})",
                                     QMessageBox.Ok)
        self._initialized = True
        self.Ui.actionRefresh.setEnabled(True)
        self.Ui.actionCheckForUpdates.setEnabled(True)
        self.Ui.modListWidget.clear()
        self.Ui.loadListWidget.clear()
        self.refreshMods(save=False)

    def refreshMods(self, *, save=True):
        if path.isdir(self._data) and path.isdir(self._mods):
            self.Ui.commitPushButton.setEnabled(True)
        else:
            self.Ui.commitPushButton.setEnabled(False)
            return
        if save:
            self.saveConfig()
        self.Ui.modListWidget.clear()
        for mod in self._modConfig["Mods"]:
            self.addModItem(*self._modConfig["Mods"][mod])
        if path.isdir(self._mods):
            for mod in listdir(self._mods):
                self.addModItem(mod)
        self.Ui.loadListWidget.clear()
        for plugin in self._modConfig["Load"]:
            self.addLoadItem(*self._modConfig["Load"][plugin])
        if path.isdir(self._data):
            for plugin in listdir(self._data):
                if plugin.endswith((".esm", ".esp", ".esl")):
                    self.addLoadItem(plugin)

    def changeModInfo(self, item):
        self.setEnabled(False)
        itemData = item.data(Qt.UserRole)
        self.dialog = EditDialog({"Name": item.text(), "Mod ID": itemData[0],
                                  "Version": itemData[1]}, self)
        if self.dialog.exec_():
            name, modID, version = self.dialog.getValues()
            if name != item.text():
                if name in listdir(self._mods):
                    QMessageBox.warning(self, "Warning", "Mod with that name "
                                        "already exists.", QMessageBox.Ok)
                else:
                    rename(path.join(self._mods, item.text()),
                           path.join(self._mods, name))
                    item.setText(name)
            item.setToolTip("ID: {}\nVersion: {}".format(modID, version))
            item.setData(Qt.UserRole, (modID, version))
        self.setEnabled(True)

    def addModItem(self, mod, check=Qt.Unchecked, modID="", version="1.0"):
        if path.isdir(path.join(self._mods, mod)):
            if not self.Ui.modListWidget.findItems(mod, Qt.MatchExactly):
                item = QListWidgetItem(mod)
                item.setData(Qt.CheckStateRole, check)
                item.setToolTip("ID: {}\nVersion: {}".format(modID, version))
                item.setData(Qt.UserRole, (modID, version))
                self.Ui.modListWidget.addItem(item)

    def addLoadItem(self, esp, check=Qt.Unchecked):
        if path.islink(path.join(self._data, esp)):
            if not self.Ui.loadListWidget.findItems(esp, Qt.MatchExactly):
                loadItem = QListWidgetItem(esp)
                loadItem.setData(Qt.CheckStateRole, check)
                self.Ui.loadListWidget.addItem(loadItem)

    @pyqtSlot()
    def selectCommit(self):
        self.refreshMods()
        if not self.Ui.commitPushButton.isEnabled():
            return
        self.Ui.commitPushButton.setEnabled(False)
        mods = []
        for index in range(self.Ui.modListWidget.count()):
            if self.Ui.modListWidget.item(index).checkState():
                mods.append(self.Ui.modListWidget.item(index).text())
        self._commiter = CommitThread(self._data, self._mods, mods, self)
        self._commiter.finished.connect(self.finishCommit)
        self._commiter.start()

    @pyqtSlot()
    def finishCommit(self):
        self.refreshMods()

    def saveConfig(self):
        if not path.isdir(self._data) and not path.isdir(self._mods):
            return
        if self.Ui.loadListWidget.count() + 5 < len(self._modConfig["Load"]):
            warn = QMessageBox.warning(self, "Warning",
                                       "Load order count varies greatly from "
                                       "config count.\n"
                                       "Do you want to skip saving?",
                                       QMessageBox.Yes | QMessageBox.No)
            if warn == QMessageBox.Yes:
                return
        self._modConfig["Mods"] = {}
        for index in range(self.Ui.modListWidget.count()):
            mod = self.Ui.modListWidget.item(index)
            self._modConfig["Mods"][index] = (mod.text(), mod.checkState()) + \
                mod.data(Qt.UserRole)
        self._modConfig["Load"] = {}
        newTime = 978300000
        for file in listdir(self._data):
            if file.endswith(".bsa"):
                try:
                    utime(path.join(self._data, file), (newTime, newTime))
                except FileNotFoundError:
                    pass
        for index in range(self.Ui.loadListWidget.count()):
            plugin = self.Ui.loadListWidget.item(index)
            self._modConfig["Load"][index] = [plugin.text(),
                                              plugin.checkState()]
            try:
                utime(path.join(self._data, plugin.text()), (newTime, newTime))
            except FileNotFoundError:
                pass
            newTime += 1
        if path.isdir(path.dirname(self._plugins)):
            with open(path.join(self._plugins), "w") as f:
                for index in range(self.Ui.loadListWidget.count()):
                    plugin = self.Ui.loadListWidget.item(index)
                    if plugin.checkState():
                        f.write(f"{self._pluginPrefix}{plugin.text()}\n")
        with open(self._config["Placer"]["config"], "w") as f:
            dump(self._modConfig, f)
        with open("placer.ini", "w") as f:
            self._config.write(f)

    def checkUpdates(self):
        self.setEnabled(False)
        updates = ""
        for index in range(self.Ui.modListWidget.count()):
            mod = self.Ui.modListWidget.item(index)
            modData = mod.data(Qt.UserRole)
            if modData[0] != "0":
                modID = modData[0].split("/")
                if len(modID) == 1:
                    modID.append(self._game)
                site = "{}/mods/{}".format(modID[1], modID[0])
                try:
                    req = Request("https://api.nexusmods.com/v1/games/"
                                  f"{site}.json", headers=self._headers)
                    with urlopen(req) as page:
                        version = load(page)["version"]
                    if modData[1] != version:
                        updates += "<a href=https://www.nexusmods.com/" \
                            f"{site}?tab=files>{mod.text()}: {modData[1]} " \
                            f"--> {version}</a><br>"
                except Exception:
                    updates += "<p>Failed opening nexus site for: " \
                        f"{mod.text()}</p><br>"
        if not updates:
            updates = "No mod updates found."
        QMessageBox.information(self, "Mod updates", updates, QMessageBox.Ok)
        self.setEnabled(True)

    def closeEvent(self, event):
        if (self._config["Placer"].getboolean("saveOnExit") and
                self._initialized):
            self.saveConfig()
        super().closeEvent(event)

    def event(self, event):
        if event.type() == QEvent.ActivationChange:
            if self.isActiveWindow():
                if (self._config["Placer"].getboolean("refreshOnFocus") and
                        self._initialized):
                    self.refreshMods()
        return super().event(event)
