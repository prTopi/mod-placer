#!/bin/python
from sys import argv
from platform import platform, python_version
from os import listdir, path, rename, symlink, mkdir, unlink
from shutil import rmtree
from json import load
from urllib.request import urlopen, Request
from configparser import ConfigParser
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QAbstractItemView, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt

__version__ = '0.1.0'

class ModDialog(QDialog):
	def __init__(self, name, modID, version, parent=None):
		super().__init__(parent)
		layout = QVBoxLayout(self)
		self.nameEdit = QLineEdit(name, self)
		self.idEdit = QLineEdit(modID, self)
		self.versEdit = QLineEdit(version, self)
		layout.addWidget(QLabel('Name', self))
		layout.addWidget(self.nameEdit)
		layout.addWidget(QLabel('Mod ID', self))
		layout.addWidget(self.idEdit)
		layout.addWidget(QLabel('Version', self))
		layout.addWidget(self.versEdit)
		buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		layout.addWidget(buttons)
		self.show()

	def getValues(self):
		return self.nameEdit.text(), self.idEdit.text(), self.versEdit.text()

class ModPlacer(QWidget):
	def __init__(self):
		super().__init__()
		self.config = ConfigParser()
		self.config.read('config.ini')
		self.headers = {'User-Agent': 'ModPlacer/{} ({}) Python/{}'.format(__version__, platform(), python_version()), 'apikey': self.config['Common']['api']}
		self.config['Common']['data'] = path.realpath(self.config['Common']['data'])
		self.config['Common']['plugins'] = path.realpath(self.config['Common']['plugins'])
		self.folder = path.dirname(path.realpath(__file__))
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
		bSave = QPushButton('Save')
		bSave.clicked.connect(self.selectSave)
		topBox = QHBoxLayout()
		topBox.addLayout(modBox)
		topBox.addLayout(loadBox)
		botBox = QHBoxLayout()
		botBox.addWidget(bRefresh)
		botBox.addWidget(bUpdates)
		botBox.addStretch(0)
		botBox.addWidget(bSave)
		layout = QVBoxLayout()
		layout.addLayout(topBox)
		layout.addLayout(botBox)
		self.setLayout(layout)
		if not self.config['Common']['api']:
			bUpdates.setEnabled(False)
		if not path.isdir(self.config['Common']['data']):
			QMessageBox.critical(self, 'Error', 'Data folder not found. ({})'.format(self.config['Common']['data']), QMessageBox.Ok)
			bRefresh.setEnabled(False)
			bSave.setEnabled(False)
		if not path.isdir(self.config['Common']['plugins']):
			QMessageBox.critical(self, 'Error', 'Plugins config folder not found. ({})'.format(self.config['Common']['data']), QMessageBox.Ok)
		if not path.isdir(path.join(self.folder, 'mods')):
			mkdir(path.join(self.folder, 'mods'))
		self.refreshMods()
		self.show()

	def refreshMods(self):
		self.saveConfig()
		self.modList.clear()
		[self.addModItem(*self.config['Mods'][mod].split('|')) for mod in self.config['Mods']]
		[self.addModItem(mod) for mod in listdir('mods')]
		self.loadOrder.clear()
		[self.addLoadItem(*self.config['LoadOrder'][esp].split('|')) for esp in self.config['LoadOrder']]
		[self.addLoadItem(esp) for esp in listdir(path.join(self.config['Common']['data'])) if esp.endswith(('.esm', '.esp', '.esl'))]

	def changeModInfo(self, item):
		self.setEnabled(False)
		iData = item.data(Qt.UserRole).split('|')
		self.dialog = ModDialog(item.text(), iData[0], iData[1], self)
		if self.dialog.exec_():
			name, modID, version = self.dialog.getValues()
			if name != item.text():
				if name in listdir(path.join(self.folder, 'mods')):
					QMessageBox.warning(self, 'Warning', 'Mod folder with that name already exists.', QMessageBox.Ok)
				else:
					rename(path.join(self.folder, 'mods', item.text()), path.join(self.folder, 'mods', name))
					item.setText(name)
			self.updateData(item, modID, version)
		self.setEnabled(True)

	def updateData(self, item, modID, version):
		item.setToolTip('ID: {}\nVersion: {}'.format(modID, version))
		item.setData(Qt.UserRole, '{}|{}'.format(modID, version))

	def addModItem(self, mod, check=Qt.Unchecked, modID='0', version='1.0'):
		if path.isdir(path.join(self.folder, 'mods', mod)):
			if not self.modList.findItems(mod, Qt.MatchExactly):
				modItem = QListWidgetItem(mod)
				modItem.setData(Qt.CheckStateRole, check)
				self.updateData(modItem, modID, version)
				self.modList.addItem(modItem)

	def addLoadItem(self, esp, check=Qt.Unchecked):
		if path.isfile(path.join(self.config['Common']['data'], esp)):
			if not self.loadOrder.findItems(esp, Qt.MatchExactly):
				loadItem = QListWidgetItem(esp)
				loadItem.setData(Qt.CheckStateRole, check)
				self.loadOrder.addItem(loadItem)

	def selectSave(self):
		self.setEnabled(False)
		self.saveConfig()
		rmtree(self.config['Common']['data'])
		mkdir(self.config['Common']['data'])
		[self.linktree(path.join(self.modList.item(index).text()), self.config['Common']['data']) for index in range(self.modList.count()) if self.modList.item(index).checkState()]
		self.refreshMods()
		self.setEnabled(True)

	def linktree(self, source, destination):
		for item in listdir(path.join(self.folder, 'mods', source)):
			src = path.join(self.folder, 'mods', source, item)
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
		self.config['Mods'] = {x: '|'.join([self.modList.item(x).text(), str(self.modList.item(x).checkState()), self.modList.item(x).data(Qt.UserRole)]) for x in range(self.modList.count())}
		self.config['LoadOrder'] = {x: '|'.join([self.loadOrder.item(x).text(), str(self.loadOrder.item(x).checkState())]) for x in range(self.loadOrder.count())}
		if path.isdir(self.config['Common']['plugins']):
			with open(path.join(self.config['Common']['plugins'], 'Plugins.txt'), 'w') as pFile:
				[pFile.write('*{}\n'.format(self.loadOrder.item(index).text())) for index in range(self.loadOrder.count()) if self.loadOrder.item(index).checkState()]
		with open('config.ini', 'w') as cFile:
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
	window = ModPlacer()
	exit(app.exec_())
