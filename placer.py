#!/usr/bin/env python3
from sys import argv
from platform import platform, python_version
from os import (listdir, path, rename, symlink, mkdir, makedirs, rmdir,
                unlink, utime)
from shutil import copy2
from json import load, dump
from urllib.request import urlopen, Request
from configparser import ConfigParser
from PyQt5.QtWidgets import (QApplication, QWidget, QDialog, QDialogButtonBox,
                             QListWidget, QListWidgetItem, QComboBox,
                             QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
                             QAbstractItemView, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt

__version__ = '0.2.5'


class ChooseConfig(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Choose Config')
        layout = QVBoxLayout(self)
        self.config = ConfigParser(defaults={'api': '', 'config': ''})
        self.config.read('placer.ini')
        self.api = QLineEdit(self.config['DEFAULT']['api'], self)
        self.configList = QComboBox(self)
        self.refresh()
        layout.addWidget(QLabel('Api Key', self))
        layout.addWidget(self.api)
        layout.addWidget(QLabel('Select Config', self))
        layout.addWidget(self.configList)
        bEdit = QPushButton('Edit', self)
        bEdit.clicked.connect(lambda: self.editConfig(
            self.configList.currentText()))
        bLoad = QPushButton('Load', self)
        bLoad.clicked.connect(self.loadConfig)
        bBox = QHBoxLayout()
        bBox.addWidget(bEdit)
        bBox.addStretch()
        bBox.addWidget(bLoad)
        layout.addLayout(bBox)
        self.setMinimumWidth(300)
        self.show()
        conf = self.config['DEFAULT']['config']
        if self.configList.findText(conf, Qt.MatchExactly) != -1:
            self.configList.setCurrentIndex(
                self.configList.findText(conf, Qt.MatchExactly))
            self.loadConfig()
        else:
            self.configList.setCurrentIndex(0)

    def refresh(self, conf=''):
        self.configList.clear()
        [self.configList.addItem(conf) for conf in listdir()
         if conf.endswith('.json')]
        self.configList.addItem('New config')
        if conf:
            if self.configList.findText(conf, Qt.MatchExactly) != -1:
                self.configList.setCurrentIndex(
                    self.configList.findText(conf, Qt.MatchExactly))
            else:
                self.configList.setCurrentIndex(0)

    def editConfig(self, name):
        self.setEnabled(False)
        if not name.endswith('.json'):
            name += '.json'
        if name in listdir():
            with open(name) as f:
                config = load(f)
        else:
            config = {'Settings': {}, 'Mods': {}, 'LoadOrder': {}}
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
            if self.configList.currentText() != name and name in listdir():
                QMessageBox.warning(self, 'File already exists',
                                    'Mod config with that name already '
                                    'exists.', QMessageBox.Ok)
                name = self.configList.currentText()
                if not name.endswith('.json'):
                    name += '.json'
            config['Settings'] = {'data': path.realpath(data), 'game': game,
                                  'mods': path.realpath(mods),
                                  'plugins': path.realpath(plugins),
                                  'pluginpref': prefix}
            config.setdefault('Mods', {})
            config.setdefault('LoadOrder', {})
            with open(name, 'w') as f:
                dump(config, f)
        self.refresh(conf=name)
        self.setEnabled(True)

    def loadConfig(self):
        self.setEnabled(False)
        confName = self.configList.currentText()
        if confName == 'New config' or confName not in listdir():
            self.editConfig(confName)
            return
        self.config['DEFAULT']['config'] = confName
        self.config['DEFAULT']['api'] = self.api.text()
        with open('placer.ini', 'w') as f:
            self.config.write(f)
        ModPlacer(confName, self.api.text(), self)
        self.hide()
        self.setEnabled(True)


class EditDialog(QDialog):
    def __init__(self, editBoxes, parent):
        super().__init__(parent)
        self.setWindowTitle('Edit Info')
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


class ModPlacer(QWidget):
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
        self.plugins = self.config['Settings'].get('plugins', 'plugins.txt')
        self.pPrefix = self.config['Settings'].get('pluginpref', '')
        self.config.setdefault('Mods', {})
        self.config.setdefault('LoadOrder', {})
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Mod Placer - ' + self.configName[:-5])
        modBox = QVBoxLayout()
        self.modList = QListWidget(self)
        self.modList.itemDoubleClicked.connect(lambda: self.changeModInfo(
            self.modList.currentItem()))
        self.modList.setDragDropMode(QAbstractItemView.InternalMove)
        self.modList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        modBox.addWidget(QLabel('Mods', self))
        modBox.addWidget(self.modList)
        loadBox = QVBoxLayout()
        self.loadList = QListWidget(self)
        self.loadList.setDragDropMode(QAbstractItemView.InternalMove)
        self.loadList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        loadBox.addWidget(QLabel('Load Order', self))
        loadBox.addWidget(self.loadList)
        bOptions = QPushButton('Options')
        bOptions.clicked.connect(lambda: self.parent.refresh(self.configName))
        bOptions.clicked.connect(self.parent.show)
        bOptions.clicked.connect(self.close)
        bUpdates = QPushButton('Check for updates')
        bUpdates.clicked.connect(self.checkUpdates)
        bRefresh = QPushButton('Refresh')
        bRefresh.clicked.connect(lambda: self.refreshMods())
        self.bSave = QPushButton('Save')
        self.bSave.clicked.connect(self.selectSave)
        topBox = QHBoxLayout()
        topBox.addLayout(modBox)
        topBox.addLayout(loadBox)
        botBox = QHBoxLayout()
        botBox.addWidget(bUpdates)
        botBox.addWidget(bOptions)
        botBox.addStretch()
        botBox.addWidget(bRefresh)
        botBox.addWidget(self.bSave)
        layout = QVBoxLayout(self)
        layout.addLayout(topBox)
        layout.addLayout(botBox)
        if not self.api:
            bUpdates.setEnabled(False)
        if not path.isdir(self.data):
            QMessageBox.critical(self, 'Error', 'Data folder not found. '
                                 f'({self.data})', QMessageBox.Ok)
            self.bSave.setEnabled(False)
        if not path.isdir(path.dirname(self.plugins)):
            QMessageBox.critical(self, 'Error', 'Plugins folder not found. '
                                 f'({path.dirname(self.plugins)})',
                                 QMessageBox.Ok)
        if not path.isdir(self.mods):
            mkdir(self.mods)
        self.resize(850, 700)
        self.refreshMods(save=False)
        self.show()

    def refreshMods(self, save=True):
        if path.isdir(self.data):
            self.bSave.setEnabled(True)
        else:
            self.bSave.setEnabled(False)
        if save:
            self.saveConfig()
        self.modList.clear()
        [self.addModItem(*self.config['Mods'][mod]) for mod
         in self.config['Mods']]
        [self.addModItem(mod) for mod in listdir(self.mods)]
        self.loadList.clear()
        [self.addLoadItem(*self.config['LoadOrder'][esp]) for esp
         in self.config['LoadOrder']]
        if path.isdir(self.data):
            [self.addLoadItem(esp) for esp in listdir(self.data)
             if esp.endswith(('.esm', '.esp', '.esl'))]

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
            if not self.modList.findItems(mod, Qt.MatchExactly):
                modItem = QListWidgetItem(mod)
                modItem.setData(Qt.CheckStateRole, check)
                self.updateData(modItem, modID, version)
                self.modList.addItem(modItem)

    def addLoadItem(self, esp, check=Qt.Unchecked):
        if path.islink(path.join(self.data, esp)):
            if not self.loadList.findItems(esp, Qt.MatchExactly):
                loadItem = QListWidgetItem(esp)
                loadItem.setData(Qt.CheckStateRole, check)
                self.loadList.addItem(loadItem)

    def selectSave(self):
        self.refreshMods()
        self.copyTree(self.data, path.join(self.mods, 'Data Backup'), rm=True)
        mkdir(self.data)
        for index in range(self.modList.count()):
            if self.modList.item(index).checkState():
                self.copyTree(path.join(self.mods,
                                        self.modList.item(index).text()),
                              self.data)
        self.refreshMods()

    def copyTree(self, source, destination, rm=False):
        for item in listdir(source):
            src = path.join(source, item)
            dst = path.join(destination, item)
            if path.isdir(src):
                if not path.isdir(dst) and not rm:
                    mkdir(dst)
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
        if self.loadList.count() + 5 < len(self.config['LoadOrder']):
            warn = QMessageBox.warning(self, 'Warning',
                                       'Load order count varies greatly from '
                                       'config count.\n'
                                       'Do you want to skip saving?',
                                       QMessageBox.Yes | QMessageBox.No)
            if warn == QMessageBox.Yes:
                return
        self.config['Mods'] = {x: (self.modList.item(x).text(),
                                   self.modList.item(x).checkState()) +
                               self.modList.item(x).data(Qt.UserRole)
                               for x in range(self.modList.count())}
        self.config['LoadOrder'] = {x: (self.loadList.item(x).text(),
                                        self.loadList.item(x).checkState())
                                    for x in range(self.loadList.count())}
        newTime = 978300000
        for x in listdir(self.data):
            if x.endswith('.bsa'):
                utime(path.join(self.data, x), (newTime, newTime))
        for x in range(self.loadList.count()):
            pluginFile = self.loadList.item(x).text()
            utime(path.join(self.data, pluginFile), (newTime, newTime))
            newTime += 1
        if path.isdir(path.dirname(self.plugins)):
            with open(path.join(self.plugins), 'w') as f:
                for index in range(self.loadList.count()):
                    if self.loadList.item(index).checkState():
                        f.write(f'{self.pPrefix}'
                                f'{self.loadList.item(index).text()}\n')
        with open(self.configName, 'w') as f:
            dump(self.config, f)

    def checkUpdates(self):
        self.setEnabled(False)
        updates = ''
        for index in range(self.modList.count()):
            mod = self.modList.item(index)
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
                        updates += '<br><a href=https://www.nexusmods.com/' \
                            f'{site}?tab=files>{mod.text()}: {modData[1]} ' \
                            f'--> {version}</a>'
                except Exception:
                    updates += '<br><p>Failed opening nexus site for: ' \
                        f'{mod.text()}</p>'
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
