#!/usr/bin/env python3
from sys import argv
from platform import platform, python_version
from os import (listdir, path, rename, symlink, makedirs, rmdir,
                unlink, utime)
from shutil import copy2
from json import load, dump
from urllib.request import urlopen, Request
from configparser import ConfigParser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog,
                             QDialogButtonBox, QListWidgetItem, QLabel,
                             QVBoxLayout, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt
from ui.options import Ui_ConfigDialog
from ui.mainwindow import Ui_MainWindow

__version__ = '0.2.5'


class ChooseConfig(QDialog):
    def __init__(self):
        super().__init__()
        self.config = ConfigParser(defaults={'api': '', 'config': ''})
        self.config.read('placer.ini')
        self.Ui = Ui_ConfigDialog()
        self.Ui.setupUi(self)
        self.Ui.lineEditApi.setText(self.config['DEFAULT']['api'])
        self.Ui.pushButtonEdit.clicked.connect(lambda: self.editConfig(
            self.Ui.comboBoxConfig.currentText()))
        self.Ui.pushButtonLoad.clicked.connect(self.loadConfig)
        self.refresh()
        self.show()
        conf = self.config['DEFAULT']['config']
        if self.Ui.comboBoxConfig.findText(conf, Qt.MatchExactly) != -1:
            self.Ui.comboBoxConfig.setCurrentIndex(
                self.Ui.comboBoxConfig.findText(conf, Qt.MatchExactly))
            self.loadConfig()
        else:
            self.Ui.comboBoxConfig.setCurrentIndex(0)

    def refresh(self, conf=''):
        self.Ui.comboBoxConfig.clear()
        for file in listdir():
            if file.endswith('.json'):
                self.Ui.comboBoxConfig.addItem(file)
        self.Ui.comboBoxConfig.addItem('New config')
        if conf:
            if self.Ui.comboBoxConfig.findText(conf, Qt.MatchExactly) != -1:
                self.Ui.comboBoxConfig.setCurrentIndex(
                    self.Ui.comboBoxConfig.findText(conf, Qt.MatchExactly))
            else:
                self.Ui.comboBoxConfig.setCurrentIndex(0)

    def editConfig(self, name):
        self.setEnabled(False)
        if not name.endswith('.json'):
            name += '.json'
        if name in listdir():
            with open(name) as f:
                config = load(f)
        else:
            config = {'Settings': {}, 'Mods': {}, 'Load': {}}
        game = config['Settings'].get('game', '')
        mods = config['Settings'].get('mods', '')
        data = config['Settings'].get('data', '')
        plugins = config['Settings'].get('plugins', '')
        prefix = config['Settings'].get('pluginpref', '')
        self.dialog = EditDialog({'File Name': name[:-5], 'Nexus Game': game,
                                  'Mods Directory': mods, 'Data Path': data,
                                  'Plugins.txt File': plugins,
                                  'Plugins.txt Line Prefix': prefix}, self)
        if self.dialog.exec_():
            name, game, mods, data, plugins, prefix = self.dialog.getValues()
            if not name.endswith('.json'):
                name += '.json'
            if (self.Ui.comboBoxConfig.currentText() != name and name in
                    listdir()):
                QMessageBox.warning(self, 'File already exists',
                                    'Mod config with that name already '
                                    'exists.', QMessageBox.Ok)
                name = self.Ui.comboBoxConfig.currentText()
                if not name.endswith('.json'):
                    name += '.json'
            config['Settings'] = {'data': path.realpath(data), 'game': game,
                                  'mods': path.realpath(mods),
                                  'plugins': path.realpath(plugins),
                                  'pluginpref': prefix}
            config.setdefault('Mods', {})
            config.setdefault('Load', {})
            with open(name, 'w') as f:
                dump(config, f)
        self.refresh(conf=name)
        self.setEnabled(True)

    def loadConfig(self):
        self.setEnabled(False)
        confName = self.Ui.comboBoxConfig.currentText()
        if confName == 'New config' or confName not in listdir():
            self.editConfig(confName)
            return
        self.config['DEFAULT']['config'] = confName
        self.config['DEFAULT']['api'] = self.Ui.lineEditApi.text()
        with open('placer.ini', 'w') as f:
            self.config.write(f)
        ModPlacer(confName, self.Ui.lineEditApi.text(), self)
        self.hide()
        self.setEnabled(True)


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


class ModPlacer(QMainWindow):
    def __init__(self, conf, api, parent):
        super().__init__()
        self.configName = conf
        self.api = api
        self.parent = parent
        self.headers = {'User-Agent': f'ModPlacer/{__version__} ({platform()})'
                        f' Python/{python_version()}', 'apikey': api}
        with open(conf) as f:
            self.config = load(f)
        self.config.setdefault('Settings', {})
        self.data = self.config['Settings'].get('data', 'Data')
        self.game = self.config['Settings'].get('game', self.configName[:-5])
        self.mods = self.config['Settings'].get('mods', 'mods')
        self.plugins = self.config['Settings'].get('plugins', '')
        self.pPrefix = self.config['Settings'].get('pluginpref', '')
        self.config.setdefault('Mods', {})
        self.config.setdefault('Load', {})
        self.Ui = Ui_MainWindow()
        self.Ui.setupUi(self)
        self.setWindowTitle(self.configName[:-5] + ' - Mod Placer')
        self.Ui.listWidgetMod.itemDoubleClicked.connect(self.changeModInfo)
        self.Ui.pushButtonOptions.clicked.connect(
            lambda: self.parent.refresh(self.configName))
        self.Ui.pushButtonOptions.clicked.connect(self.parent.show)
        self.Ui.pushButtonOptions.clicked.connect(self.close)
        self.Ui.pushButtonUpdate.clicked.connect(self.checkUpdates)
        self.Ui.actionRefresh.triggered.connect(self.refreshMods)
        self.Ui.pushButtonSave.clicked.connect(self.selectSave)
        if not self.api:
            self.Ui.pushButtonUpdate.setEnabled(False)
        if not path.isdir(self.data):
            QMessageBox.critical(self, 'Error', 'Data folder not found.'
                                 f' ({self.data})', QMessageBox.Ok)
            self.Ui.pushButtonSave.setEnabled(False)
        if self.plugins != '':
            if not path.isdir(path.dirname(self.plugins)):
                QMessageBox.critical(self, 'Error', 'Plugins folder not found.'
                                     f' ({path.dirname(self.plugins)})',
                                     QMessageBox.Ok)
        if not path.isdir(self.mods):
            makedirs(self.mods)
        self.refreshMods(save=False)
        self.show()

    def refreshMods(self, *, save=True):
        if path.isdir(self.data):
            self.Ui.pushButtonSave.setEnabled(True)
        else:
            self.Ui.pushButtonSave.setEnabled(False)
        if save:
            self.saveConfig()
        self.Ui.listWidgetMod.clear()
        for mod in self.config['Mods']:
            self.addModItem(*self.config['Mods'][mod])
        for mod in listdir(self.mods):
            self.addModItem(mod)
        self.Ui.listWidgetLoad.clear()
        for plugin in self.config['Load']:
            self.addLoadItem(*self.config['Load'][plugin])
        if path.isdir(self.data):
            for plugin in listdir(self.data):
                if plugin.endswith(('.esm', '.esp', '.esl')):
                    self.addLoadItem(plugin)

    def changeModInfo(self, item):
        self.setEnabled(False)
        iData = item.data(Qt.UserRole)
        self.dialog = EditDialog({'Name': item.text(), 'Mod ID': iData[0],
                                  'Version': iData[1]}, self)
        if self.dialog.exec_():
            name, modID, version = self.dialog.getValues()
            if name != item.text():
                if name in listdir(self.mods):
                    QMessageBox.warning(self, 'Warning', 'Mod with that name '
                                        'already exists.', QMessageBox.Ok)
                else:
                    rename(path.join(self.mods, item.text()),
                           path.join(self.mods, name))
                    item.setText(name)
            self.updateData(item, modID, version)
        self.setEnabled(True)

    def updateData(self, item, modID, version):
        item.setToolTip('ID: {}\nVersion: {}'.format(modID, version))
        item.setData(Qt.UserRole, (modID, version))

    def addModItem(self, mod, check=Qt.Unchecked, modID='0', version='1.0'):
        if path.isdir(path.join(self.mods, mod)):
            if not self.Ui.listWidgetMod.findItems(mod, Qt.MatchExactly):
                modItem = QListWidgetItem(mod)
                modItem.setData(Qt.CheckStateRole, check)
                self.updateData(modItem, modID, version)
                self.Ui.listWidgetMod.addItem(modItem)

    def addLoadItem(self, esp, check=Qt.Unchecked):
        if path.islink(path.join(self.data, esp)):
            if not self.Ui.listWidgetLoad.findItems(esp, Qt.MatchExactly):
                loadItem = QListWidgetItem(esp)
                loadItem.setData(Qt.CheckStateRole, check)
                self.Ui.listWidgetLoad.addItem(loadItem)

    def selectSave(self):
        self.refreshMods()
        self.copyTree(self.data, path.join(self.mods, 'Data Backup'), rm=True)
        makedirs(self.data)
        for index in range(self.Ui.listWidgetMod.count()):
            if self.Ui.listWidgetMod.item(index).checkState():
                folder = self.Ui.listWidgetMod.item(index).text()
                self.copyTree(path.join(self.mods, folder), self.data)
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
        if self.Ui.listWidgetLoad.count() + 5 < len(self.config['Load']):
            warn = QMessageBox.warning(self, 'Warning',
                                       'Load order count varies greatly from '
                                       'config count.\n'
                                       'Do you want to skip saving?',
                                       QMessageBox.Yes | QMessageBox.No)
            if warn == QMessageBox.Yes:
                return
        self.config['Mods'] = {}
        for index in range(self.Ui.listWidgetMod.count()):
            mod = self.Ui.listWidgetMod.item(index)
            self.config['Mods'][index] = (mod.text(), mod.checkState()) + \
                mod.data(Qt.UserRole)
        self.config['Load'] = {}
        newTime = 978300000
        for file in listdir(self.data):
            if file.endswith('.bsa'):
                try:
                    utime(path.join(self.data, file), (newTime, newTime))
                except FileNotFoundError:
                    pass
        for index in range(self.Ui.listWidgetLoad.count()):
            plugin = self.Ui.listWidgetLoad.item(index)
            self.config['Load'][index] = [plugin.text(), plugin.checkState()]
            try:
                utime(path.join(self.data, plugin.text()), (newTime, newTime))
            except FileNotFoundError:
                pass
            newTime += 1
        if path.isdir(path.dirname(self.plugins)):
            with open(path.join(self.plugins), 'w') as f:
                for index in range(self.Ui.listWidgetLoad.count()):
                    plugin = self.Ui.listWidgetLoad.item(index)
                    if plugin.checkState():
                        f.write(f'{self.pPrefix}{plugin.text()}\n')
        with open(self.configName, 'w') as f:
            dump(self.config, f)

    def checkUpdates(self):
        self.setEnabled(False)
        updates = ''
        for index in range(self.Ui.listWidgetMod.count()):
            mod = self.Ui.listWidgetMod.item(index)
            modData = mod.data(Qt.UserRole)
            if modData[0] != '0':
                modID = modData[0].split('/')
                if len(modID) == 1:
                    modID.append(self.game)
                site = '{}/mods/{}'.format(modID[1], modID[0])
                try:
                    with urlopen(Request('https://api.nexusmods.com/v1/games/'
                                         f'{site}.json',
                                         headers=self.headers)) as page:
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


if __name__ == '__main__':
    app = QApplication(argv)
    window = ChooseConfig()
    exit(app.exec_())
