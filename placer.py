#!/bin/python
from sys import argv
from platform import platform, python_version
from os import listdir, path, rename, symlink, mkdir, unlink
from shutil import rmtree
from json import load
from urllib.request import urlopen, Request
from configparser import ConfigParser
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem, QComboBox, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QAbstractItemView, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt

__version__ = '0.2.3'

class ChooseConfig(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Choose Config')
		layout = QVBoxLayout(self)
		self.config = ConfigParser()
		self.config.read('config.ini')
		self.api = QLineEdit(self.config.get('DEFAULT', 'api', fallback=''), self)
		self.configList = QComboBox(self)
		self.refresh()
		layout.addWidget(QLabel('Api Key', self))
		layout.addWidget(self.api)
		layout.addWidget(QLabel('Select Config', self))
		layout.addWidget(self.configList)
		bEdit = QPushButton('Edit', self)
		bEdit.clicked.connect(lambda: self.editConfig(self.configList.currentText()))
		bLoad = QPushButton('Load', self)
		bLoad.clicked.connect(self.loadConfig)
		bBox = QHBoxLayout()
		bBox.addWidget(bEdit)
		bBox.addStretch(1)
		bBox.addWidget(bLoad)
		layout.addLayout(bBox)
		self.setMinimumWidth(300)
		self.show()
		conf = self.config.get('DEFAULT', 'config', fallback='')
		if self.configList.findText(conf, Qt.MatchExactly) != -1:
			self.configList.setCurrentIndex(self.configList.findText(conf, Qt.MatchExactly))
			self.loadConfig()
		else:
			self.configList.setCurrentIndex(0)

	def refresh(self):
		self.configList.clear()
		[self.configList.addItem(conf) for conf in listdir() if conf.endswith('.ini') and conf != 'config.ini']
		self.configList.addItem('New config')
		conf = self.config.get('DEFAULT', 'config', fallback='')
		if self.configList.findText(conf, Qt.MatchExactly) != -1:
			self.configList.setCurrentIndex(self.configList.findText(conf, Qt.MatchExactly))
		else:
			self.configList.setCurrentIndex(0)

	def editConfig(self, name):
		self.setEnabled(False)
		config = ConfigParser()
		config.read(name)
		game = self.config.get('Common', 'game', fallback='')
		mods = self.config.get('Common', 'mods', fallback='')
		data = self.config.get('Common', 'data', fallback='')
		plugins = self.config.get('Common', 'plugins', fallback='')
		prefix = self.config.get('Common', 'pluginpref', fallback='')
		self.dialog = EditDialog({'File Name': name[:-4], 'Nexus Game': game, 'Mods Directory': mods, 'Data Path': data, 'Plugins.txt File': plugins, 'Plugins.txt Line Prefix': prefix}, self)
		if self.dialog.exec_():
			name, game, mods, data, plugins, prefix = self.dialog.getValues()
			name += '.ini'
			if self.configList.currentText() != name and name in listdir():
				QMessageBox.information(self, 'File already exists', 'Mod config with that name already exists.', QMessageBox.Ok)
				return
			config['Common'] = {'data': path.realpath(data), 'game': game, 'mods': path.realpath(mods), 'plugins': path.realpath(plugins), 'pluginpref': prefix}
			if not config.has_section('Mods'):
				config.add_section('Mods')
			if not config.has_section('LoadOrder'):
				config.add_section('LoadOrder')
			with open(name, 'w') as cFile:
				config.write(cFile)
		self.refresh()
		self.configList.setCurrentIndex(self.configList.findText(name, Qt.MatchExactly))
		self.setEnabled(True)

	def loadConfig(self):
		self.setEnabled(False)
		confName = self.configList.currentText()
		if confName == 'New config' or confName not in listdir():
			self.editConfig(confName)
			return
		self.config['DEFAULT']['config'] = confName
		self.config['DEFAULT']['api'] = self.api.text()
		with open('config.ini', 'w') as cFile:
			self.config.write(cFile)
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
		buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
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
		self.config = ConfigParser()
		self.config.read(conf)
		self.api = api
		self.parent = parent
		self.headers = {'User-Agent': 'ModPlacer/{} ({}) Python/{}'.format(__version__, platform(), python_version()), 'apikey': self.api}
		self.folder = path.dirname(path.realpath(__file__))
		self.data = self.config.get('Common', 'data', fallback='Data')
		self.game = self.config.get('Common', 'game', fallback=self.configName[:-4])
		self.mods = self.config.get('Common', 'mods', fallback='mods')
		self.plugins = self.config.get('Common', 'plugins', fallback='plugins.txt')
		self.pPrefix = self.config.get('Common', 'pPrefix', fallback='')
		if not self.config.has_section('Mods'):
			self.config.add_section('Mods')
		self.modOrder = self.config['Mods']
		if not self.config.has_section('LoadOrder'):
			self.config.add_section('LoadOrder')
		self.loadOrder = self.config['LoadOrder']
		self.initUI()

	def initUI(self):
		self.setWindowTitle('Mod Placer - ' + self.configName[:-4])
		modBox = QVBoxLayout()
		self.modList = QListWidget(self)
		self.modList.itemDoubleClicked.connect(lambda: self.changeModInfo(self.modList.currentItem()))
		self.modList.setDragDropMode(QAbstractItemView.InternalMove)
		modBox.addWidget(QLabel('Mods', self))
		modBox.addWidget(self.modList)
		loadBox = QVBoxLayout()
		self.loadList = QListWidget(self)
		self.loadList.setDragDropMode(QAbstractItemView.InternalMove)
		loadBox.addWidget(QLabel('Load Order', self))
		loadBox.addWidget(self.loadList)
		bOptions = QPushButton('Options')
		bOptions.clicked.connect(self.parent.refresh)
		bOptions.clicked.connect(self.parent.show)
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
			QMessageBox.critical(self, 'Error', 'Data folder not found. ({})'.format(self.data), QMessageBox.Ok)
			self.bSave.setEnabled(False)
		if not path.isdir(path.dirname(self.plugins)):
			QMessageBox.critical(self, 'Error', 'Plugins config folder not found. ({})'.format(path.dirname(self.plugins)), QMessageBox.Ok)
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
		[self.addModItem(*self.modOrder[mod].split('|')) for mod in self.modOrder]
		[self.addModItem(mod) for mod in listdir(self.mods)]
		self.loadList.clear()
		[self.addLoadItem(*self.loadOrder[esp].split('|')) for esp in self.loadOrder]
		if path.isdir(self.data):
			[self.addLoadItem(esp) for esp in listdir(self.data) if esp.endswith(('.esm', '.esp', '.esl'))]

	def changeModInfo(self, item):
		self.setEnabled(False)
		iData = item.data(Qt.UserRole).split('|')
		self.dialog = EditDialog({'Name': item.text(), 'Mod ID': iData[0], 'Version': iData[1]}, self)
		if self.dialog.exec_():
			name, modID, version = self.dialog.getValues()
			if name != item.text():
				if name in listdir(self.mods):
					QMessageBox.warning(self, 'Warning', 'Mod folder with that name already exists.', QMessageBox.Ok)
				else:
					rename(path.join(self.mods, item.text()), path.join(self.mods, name))
					item.setText(name)
			self.updateData(item, modID, version)
		self.setEnabled(True)

	def updateData(self, item, modID, version):
		item.setToolTip('ID: {}\nVersion: {}'.format(modID, version))
		item.setData(Qt.UserRole, '{}|{}'.format(modID, version))

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
		rmtree(self.data)
		mkdir(self.data)
		[self.linktree(self.modList.item(index).text(), self.data) for index in range(self.modList.count()) if self.modList.item(index).checkState()]
		self.refreshMods()

	def linktree(self, source, destination):
		for item in listdir(path.join(self.mods, source)):
			src = path.join(self.mods, source, item)
			dst = path.join(destination, item)
			if path.isdir(src):
				if not path.isdir(dst):
					mkdir(dst)
				self.linktree(src, dst)
			else:
				if path.islink(dst):
					unlink(dst)
				symlink(src, dst)

	def saveConfig(self):
		if self.loadList.count() + 5 < len(self.loadOrder):
			if QMessageBox.warning(self, 'Warning', 'Load order count varies greatly from config count.\nDo you want to skip saving?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
				return
		self.config['Mods'] = {x: '|'.join([self.modList.item(x).text(), str(self.modList.item(x).checkState()), self.modList.item(x).data(Qt.UserRole)]) for x in range(self.modList.count())}
		self.config['LoadOrder'] = {x: '|'.join([self.loadList.item(x).text(), str(self.loadList.item(x).checkState())]) for x in range(self.loadList.count())}
		self.modOrder = self.config['Mods']
		self.loadOrder = self.config['LoadOrder']
		if path.isdir(path.dirname(self.plugins)):
			with open(path.join(self.plugins), 'w') as pFile:
				[pFile.write('{}{}\n'.format(self.pPrefix, self.loadList.item(index).text())) for index in range(self.loadList.count()) if self.loadList.item(index).checkState()]
		with open(self.configName, 'w') as cFile:
			self.config.write(cFile)

	def checkUpdates(self):
		self.setEnabled(False)
		updates = ''
		for index in range(self.modList.count()):
			mod = self.modList.item(index)
			modData = mod.data(Qt.UserRole).split('|')
			if modData[0] != '0':
				modID = modData[0].split('/')
				if len(modID) == 1:
					modID.append(self.game)
				with urlopen(Request('https://api.nexusmods.com/v1/games/{}/mods/{}.json'.format(modID[1], modID[0]), headers=self.headers)) as page:
					version = load(page)['version']
				if modData[1] != version:
					updates += '\n{}: {} --> {}'.format(mod.text(), modData[1], version)
		self.setEnabled(True)
		if not updates:
			updates = 'No mod updates found.'
		QMessageBox.information(self, 'Mod updates', 'Mod updates:\n' + updates, QMessageBox.Ok)

	def closeEvent(self, event):
		self.saveConfig()

if __name__ == '__main__':
	app = QApplication(argv)
	window = ChooseConfig()
	exit(app.exec_())
