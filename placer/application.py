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
from PyQt5.QtCore import Qt, QEvent
from placer.ui.mainwindow import Ui_MainWindow
from placer.options import OptionsDialog
from placer.edit import EditDialog

__version__ = "0.2.7"


class ModPlacer(QMainWindow):
    def __init__(self):
        super().__init__()
        self._config = ConfigParser(defaults={'api': '', 'config': ''})
        self._config.read('placer.ini')
        self.Ui = Ui_MainWindow()
        self.Ui.setupUi(self)
        self.Ui.listWidgetMod.itemDoubleClicked.connect(self.changeModInfo)
        self.Ui.pushButtonSave.clicked.connect(self.selectSave)
        self.Ui.actionOptions.triggered.connect(self.loadConfig)
        self.Ui.actionCheckForUpdates.triggered.connect(self.checkUpdates)
        self.Ui.actionRefresh.triggered.connect(self.refreshMods)
        self.Ui.actionQuit.triggered.connect(self.close)
        self.show()
        self.loadConfig(config=self._config['DEFAULT']['config'])

    def loadConfig(self, *, config=''):
        self.setEnabled(False)
        api = self._config['DEFAULT']['api']
        if config == '':
            config = self._config['DEFAULT']['config']
            dialog = OptionsDialog(config, api, self)
            if dialog.exec_():
                api, config = dialog.getValues()
            else:
                if not self._config['DEFAULT']['config']:
                    self.close()
                self.setEnabled(True)
                return
        self._config['DEFAULT']['config'] = config
        try:
            with open(config + '.json') as f:
                self._modConfig = load(f)
        except FileNotFoundError:
            self._modConfig = {}
        self._modConfig.setdefault('Settings', {})
        self._data = self._modConfig['Settings'].get('data', 'Data')
        self._game = self._modConfig['Settings'].get('game', config)
        self._mods = self._modConfig['Settings'].get('mods', 'mods')
        self._plugins = self._modConfig['Settings'].get('plugins', '')
        self._pPrefix = self._modConfig['Settings'].get('pluginpref', '')
        self._modConfig.setdefault('Mods', {})
        self._modConfig.setdefault('Load', {})
        self.setWindowTitle(config + ' - Mod Placer')
        if api:
            self.Ui.actionCheckForUpdates.setEnabled(True)
            self._headers = {'User-Agent': f'ModPlacer/{__version__} '
                             f'({system()} {release()}) '
                             f'Python/{python_version()}', 'apikey': api}
        else:
            self.Ui.actionCheckForUpdates.setEnabled(False)
        if self._plugins != '':
            if not path.isdir(path.dirname(self._plugins)):
                QMessageBox.critical(self, 'Error', 'Plugins folder not found.'
                                     f' ({path.dirname(self._plugins)})',
                                     QMessageBox.Ok)
        self.refreshMods(save=False)
        self.setEnabled(True)

    def refreshMods(self, *, save=True):
        if path.isdir(self._data) and path.isdir(self._data):
            self.Ui.pushButtonSave.setEnabled(True)
        else:
            self.Ui.pushButtonSave.setEnabled(False)
        if save:
            self.saveConfig()
        self.Ui.listWidgetMod.clear()
        for mod in self._modConfig['Mods']:
            self.addModItem(*self._modConfig['Mods'][mod])
        if path.isdir(self._mods):
            for mod in listdir(self._mods):
                self.addModItem(mod)
        self.Ui.listWidgetLoad.clear()
        for plugin in self._modConfig['Load']:
            self.addLoadItem(*self._modConfig['Load'][plugin])
        if path.isdir(self._data):
            for plugin in listdir(self._data):
                if plugin.endswith(('.esm', '.esp', '.esl')):
                    self.addLoadItem(plugin)

    def changeModInfo(self, item):
        self.setEnabled(False)
        itemData = item.data(Qt.UserRole)
        self.dialog = EditDialog({'Name': item.text(), 'Mod ID': itemData[0],
                                  'Version': itemData[1]}, self)
        if self.dialog.exec_():
            name, modID, version = self.dialog.getValues()
            if name != item.text():
                if name in listdir(self._mods):
                    QMessageBox.warning(self, 'Warning', 'Mod with that name '
                                        'already exists.', QMessageBox.Ok)
                else:
                    rename(path.join(self._mods, item.text()),
                           path.join(self._mods, name))
                    item.setText(name)
            self.updateData(item, modID, version)
        self.setEnabled(True)

    def updateData(self, item, modID, version):
        item.setToolTip('ID: {}\nVersion: {}'.format(modID, version))
        item.setData(Qt.UserRole, (modID, version))

    def addModItem(self, mod, check=Qt.Unchecked, modID='', version='1.0'):
        if path.isdir(path.join(self._mods, mod)):
            if not self.Ui.listWidgetMod.findItems(mod, Qt.MatchExactly):
                modItem = QListWidgetItem(mod)
                modItem.setData(Qt.CheckStateRole, check)
                self.updateData(modItem, modID, version)
                self.Ui.listWidgetMod.addItem(modItem)

    def addLoadItem(self, esp, check=Qt.Unchecked):
        if path.islink(path.join(self._data, esp)):
            if not self.Ui.listWidgetLoad.findItems(esp, Qt.MatchExactly):
                loadItem = QListWidgetItem(esp)
                loadItem.setData(Qt.CheckStateRole, check)
                self.Ui.listWidgetLoad.addItem(loadItem)

    def selectSave(self):
        self.refreshMods()
        self.copyTree(self._data, path.join(self._mods, 'Data Backup'),
                      rm=True)
        makedirs(self._data, exist_ok=True)
        for index in range(self.Ui.listWidgetMod.count()):
            if self.Ui.listWidgetMod.item(index).checkState():
                folder = self.Ui.listWidgetMod.item(index).text()
                self.copyTree(path.join(self._mods, folder), self._data)
        self.refreshMods()

    def copyTree(self, source, destination, rm=False):
        for item in listdir(source):
            src = path.join(source, item)
            dst = path.join(destination, item)
            if path.isdir(src):
                if not path.isdir(dst) and not rm:
                    makedirs(dst)
                self.copyTree(src, dst, rm)
            else:
                if path.islink(dst):
                    unlink(dst)
                if rm:
                    if path.isfile(src) and not path.islink(src):
                        makedirs(path.dirname(dst), exist_ok=True)
                        copy2(src, dst)
                    unlink(src)
                else:
                    symlink(src, dst)
        if rm:
            rmdir(source)

    def saveConfig(self):
        if self.Ui.listWidgetLoad.count() + 5 < len(self._modConfig['Load']):
            warn = QMessageBox.warning(self, 'Warning',
                                       'Load order count varies greatly from '
                                       'config count.\n'
                                       'Do you want to skip saving?',
                                       QMessageBox.Yes | QMessageBox.No)
            if warn == QMessageBox.Yes:
                return
        self._modConfig['Mods'] = {}
        for index in range(self.Ui.listWidgetMod.count()):
            mod = self.Ui.listWidgetMod.item(index)
            self._modConfig['Mods'][index] = (mod.text(), mod.checkState()) + \
                mod.data(Qt.UserRole)
        self._modConfig['Load'] = {}
        newTime = 978300000
        for file in listdir(self._data):
            if file.endswith('.bsa'):
                try:
                    utime(path.join(self._data, file), (newTime, newTime))
                except FileNotFoundError:
                    pass
        for index in range(self.Ui.listWidgetLoad.count()):
            plugin = self.Ui.listWidgetLoad.item(index)
            self._modConfig['Load'][index] = [plugin.text(),
                                              plugin.checkState()]
            try:
                utime(path.join(self._data, plugin.text()), (newTime, newTime))
            except FileNotFoundError:
                pass
            newTime += 1
        if path.isdir(path.dirname(self._plugins)):
            with open(path.join(self._plugins), 'w') as f:
                for index in range(self.Ui.listWidgetLoad.count()):
                    plugin = self.Ui.listWidgetLoad.item(index)
                    if plugin.checkState():
                        f.write(f'{self._pPrefix}{plugin.text()}\n')
        with open(self._config['DEFAULT']['config'] + '.json', 'w') as f:
            dump(self._modConfig, f)
        with open('placer.ini', 'w') as f:
            self._config.write(f)

    def checkUpdates(self):
        self.setEnabled(False)
        updates = ''
        for index in range(self.Ui.listWidgetMod.count()):
            mod = self.Ui.listWidgetMod.item(index)
            modData = mod.data(Qt.UserRole)
            if modData[0] != '0':
                modID = modData[0].split('/')
                if len(modID) == 1:
                    modID.append(self._game)
                site = '{}/mods/{}'.format(modID[1], modID[0])
                try:
                    req = Request('https://api.nexusmods.com/v1/games/'
                                  f'{site}.json', headers=self._headers)
                    with urlopen(req) as page:
                        version = load(page)['version']
                    if modData[1] != version:
                        updates += '<a href=https://www.nexusmods.com/' \
                            f'{site}?tab=files>{mod.text()}: {modData[1]} ' \
                            f'--> {version}</a><br>'
                except Exception:
                    updates += '<p>Failed opening nexus site for: ' \
                        f'{mod.text()}</p><br>'
        if not updates:
            updates = 'No mod updates found.'
        QMessageBox.information(self, 'Mod updates', updates, QMessageBox.Ok)
        self.setEnabled(True)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.saveConfig()

    def event(self, event):
        if event.type() == QEvent.ActivationChange:
            if self.isActiveWindow():
                self.refreshMods()
        return super().event(event)


if __name__ == '__main__':
    app = QApplication(argv)
    window = ModPlacer()
    exit(app.exec_())
