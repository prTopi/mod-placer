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

__version__ = '0.2.2'

class ChooseConfig(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Choose Config')
		layout = QVBoxLayout(self)
		self.config = ConfigParser()
		self.selectedConfig = ''
		if path.isfile('config.ini'):
			self.config.read('config.ini')
		else:
			self.config['DEFAULT'] = {'api': '', 'config': ''}
		self.api = QLineEdit(self.config['DEFAULT']['api'], self)
		self.configList = QComboBox(self)
		[self.configList.addItem(conf) for conf in listdir() if conf.endswith('.ini') and conf != 'config.ini']
		self.configList.addItem('New config')
		layout.addWidget(QLabel('Api Key', self))
		layout.addWidget(self.api)
		layout.addWidget(QLabel('Select Config', self))
		layout.addWidget(self.configList)
		buttons = QDialogButtonBox(QDialogButtonBox.Ok, Qt.Horizontal, self)
		buttons.accepted.connect(self.loadConfig)
		layout.addWidget(buttons)
		self.show()
		conf = self.config['DEFAULT']['config']
		if conf in listdir() and conf.endswith('.ini') and conf != 'config.ini':
			self.selectedConfig = conf
			self.loadConfig()

	def loadConfig(self):
		self.setEnabled(False)
		if not self.selectedConfig:
			self.selectedConfig = self.configList.currentText()
		if self.configList.currentText() == 'New config':
			self.dialog = EditDialog((('Config Name', ''), ('Nexus Game', ''), ('Mods Directory', ''), ('Data Path', ''), ('Plugins.txt File', ''), ('Plugins.txt Line Prefix', '')), self)
			if self.dialog.exec_():
				name, game, mods, data, plugins, prefix = self.dialog.getValues()
				newConfig = ConfigParser()
				newConfig['Common'] = {'data': path.realpath(data), 'game': game, 'mods': path.realpath(mods), 'plugins': path.realpath(plugins), 'pluginpref': prefix}
				newConfig['Mods'] = {}
				newConfig['LoadOrder'] = {}
				with open(name + '.ini', 'w') as cFile:
					newConfig.write(cFile)
				self.selectedConfig = name + '.ini'
		self.config['DEFAULT']['config'] = self.selectedConfig
		self.config['DEFAULT']['api'] = self.api.text()
		with open('config.ini', 'w') as cFile:
			self.config.write(cFile)
		ModPlacer(self.selectedConfig, self.api.text(), self)
		self.selectedConfig = ''
		self.hide()
		self.setEnabled(True)

class EditDialog(QDialog):
	def __init__(self, editBoxes, parent):
		super().__init__(parent)
		self.setWindowTitle('Edit Info')
		layout = QVBoxLayout(self)
		for box in editBoxes:
			layout.addWidget(QLabel(box[0], self))
			layout.addWidget(QLineEdit(box[1], self))
		buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		layout.addWidget(buttons)
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
		self.data = self.config['Common']['data']
		self.mods = self.config['Common']['mods']
		self.plugins = self.config['Common']['plugins']
		self.pPrefix = self.config['Common']['pluginPref']
		self.initUI()

	def initUI(self):
		self.resize(850, 700)
		self.setWindowTitle('Mod Placer')
		modBox = QVBoxLayout()
		self.modList = QListWidget(self)
		self.modList.itemDoubleClicked.connect(lambda: self.changeModInfo(self.modList.currentItem()))
		self.modList.setDragDropMode(QAbstractItemView.InternalMove)
		[self.addModItem(*self.config['Mods'][mod].split('|')) for mod in self.config['Mods']]
		modBox.addWidget(QLabel('Mods', self))
		modBox.addWidget(self.modList)
		loadBox = QVBoxLayout()
		self.loadOrder = QListWidget(self)
		self.loadOrder.setDragDropMode(QAbstractItemView.InternalMove)
		[self.addLoadItem(*self.config['LoadOrder'][esp].split('|')) for esp in self.config['LoadOrder']]
		loadBox.addWidget(QLabel('Load Order', self))
		loadBox.addWidget(self.loadOrder)
		bRefresh = QPushButton('Refresh')
		bRefresh.clicked.connect(self.refreshMods)
		bUpdates = QPushButton('Check for updates')
		bUpdates.clicked.connect(self.checkUpdates)
		bOptions = QPushButton('Options')
		bOptions.clicked.connect(self.parent.show)
		bOptions.clicked.connect(self.close)
		bSave = QPushButton('Save')
		bSave.clicked.connect(self.selectSave)
		topBox = QHBoxLayout()
		topBox.addLayout(modBox)
		topBox.addLayout(loadBox)
		botBox = QHBoxLayout()
		botBox.addWidget(bRefresh)
		botBox.addWidget(bUpdates)
		botBox.addStretch(1)
		botBox.addWidget(bOptions)
		botBox.addStretch(2)
		botBox.addWidget(bSave)
		layout = QVBoxLayout(self)
		layout.addLayout(topBox)
		layout.addLayout(botBox)
		if not self.api:
			bUpdates.setEnabled(False)
		if not path.isdir(self.data):
			QMessageBox.critical(self, 'Error', 'Data folder not found. ({})'.format(self.data), QMessageBox.Ok)
			bRefresh.setEnabled(False)
			bSave.setEnabled(False)
		if not path.isdir(path.dirname(self.plugins)):
			QMessageBox.critical(self, 'Error', 'Plugins config folder not found. ({})'.format(path.isdir(path.dirname(self.plugins))), QMessageBox.Ok)
		if not path.isdir(self.mods):
			mkdir(self.mods)
		self.show()
		self.refreshMods()

	def refreshMods(self):
		self.saveConfig()
		self.modList.clear()
		[self.addModItem(*self.config['Mods'][mod].split('|')) for mod in self.config['Mods']]
		[self.addModItem(mod) for mod in listdir(self.mods)]
		self.loadOrder.clear()
		[self.addLoadItem(*self.config['LoadOrder'][esp].split('|')) for esp in self.config['LoadOrder']]
		[self.addLoadItem(esp) for esp in listdir(self.data) if esp.endswith(('.esm', '.esp', '.esl'))]

	def changeModInfo(self, item):
		self.setEnabled(False)
		iData = item.data(Qt.UserRole).split('|')
		self.dialog = EditDialog((('Name', item.text()), ('Mod ID', iData[0]), ('Version', iData[1])), self)
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
			if not self.loadOrder.findItems(esp, Qt.MatchExactly):
				loadItem = QListWidgetItem(esp)
				loadItem.setData(Qt.CheckStateRole, check)
				self.loadOrder.addItem(loadItem)

	def selectSave(self):
		self.setEnabled(False)
		self.saveConfig()
		rmtree(self.data)
		mkdir(self.data)
		[self.linktree(self.modList.item(index).text(), self.data) for index in range(self.modList.count()) if self.modList.item(index).checkState()]
		self.refreshMods()
		self.setEnabled(True)

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
		if self.loadOrder.count() + 5 < len(self.config['LoadOrder']):
			if QMessageBox.warning(self, 'Warning', 'Load order count varies greatly from config count.\nDo you want to skip saving?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
				return
		self.config['Mods'] = {x: '|'.join([self.modList.item(x).text(), str(self.modList.item(x).checkState()), self.modList.item(x).data(Qt.UserRole)]) for x in range(self.modList.count())}
		self.config['LoadOrder'] = {x: '|'.join([self.loadOrder.item(x).text(), str(self.loadOrder.item(x).checkState())]) for x in range(self.loadOrder.count())}
		if path.isdir(path.dirname(self.plugins)):
			with open(path.join(self.plugins), 'w') as pFile:
				[pFile.write('{}{}\n'.format(self.pPrefix, self.loadOrder.item(index).text())) for index in range(self.loadOrder.count()) if self.loadOrder.item(index).checkState()]
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
					modID.append(self.config['Common']['game'])
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
