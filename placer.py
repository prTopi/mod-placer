#!/bin/python
from sys import argv
from platform import platform, python_version
from os import listdir, system, path, rename
from json import load
from urllib.request import urlopen, Request
from configparser import ConfigParser
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QAbstractItemView, QListWidgetItem, QInputDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt

__version__ = '0.1.0'

class ModPlacer(QWidget):
	def __init__(self):
		super().__init__()
		self.config = ConfigParser()
		self.config.read('config.ini')
		self.headers = {'User-Agent': 'ModPlacer/{} ({}) Python/{}'.format(__version__, platform(), python_version()), 'apikey': self.config['Common']['api']}
		self.folder = path.dirname(path.realpath(__file__))
		self.initUI()

	def initUI(self):
		self.resize(750, 600)
		self.setWindowTitle('Mod Placer')
		bRefresh = QPushButton('Refresh')
		bRefresh.clicked.connect(self.refreshMods)
		bUpdates = QPushButton('Check for updates')
		bUpdates.clicked.connect(self.checkUpdates)
		if not self.config['Common']['api']:
			bUpdates.setEnabled(False)
		modBox = QVBoxLayout()
		self.modList = QListWidget(self)
		self.modList.itemDoubleClicked.connect(lambda: self.changeModInfo(self.modList.currentItem()))
		self.modList.setDragDropMode(QAbstractItemView.InternalMove)
		self.modList.setSelectionMode(QAbstractItemView.SingleSelection)
		[self.addModItem(*self.config['Mods'][mod].split('|')) for mod in self.config['Mods']]
		modBox.addWidget(QLabel('Mods', self))
		modBox.addWidget(self.modList)
		loadBox = QVBoxLayout()
		self.loadOrder = QListWidget(self)
		self.loadOrder.setDragDropMode(QAbstractItemView.InternalMove)
		self.loadOrder.setSelectionMode(QAbstractItemView.SingleSelection)
		[self.addLoadItem(*self.config['LoadOrder'][esp].split('|')) for esp in self.config['LoadOrder']]
		loadBox.addWidget(QLabel('Load Order', self))
		loadBox.addWidget(self.loadOrder)
		bSave = QPushButton('Save')
		bSave.clicked.connect(self.selectSave)
		topBox = QHBoxLayout()
		topBox.addWidget(bUpdates)
		topBox.addStretch(0)
		topBox.addWidget(bRefresh)
		midBox = QHBoxLayout()
		midBox.addLayout(modBox)
		midBox.addLayout(loadBox)
		botBox = QHBoxLayout()
		botBox.addStretch(0)
		botBox.addWidget(bSave)
		layout = QVBoxLayout()
		layout.addLayout(topBox)
		layout.addLayout(midBox)
		layout.addLayout(botBox)
		self.setLayout(layout)
		self.refreshMods()
		self.show()

	def refreshMods(self):
		self.saveConfig()
		self.modList.clear()
		[self.addModItem(*self.config['Mods'][mod].split('|')) for mod in self.config['Mods']]
		[self.addModItem(mod) for mod in listdir('mods')]
		self.loadOrder.clear()
		[self.addLoadItem(*self.config['LoadOrder'][esp].split('|')) for esp in self.config['LoadOrder']]
		[self.addLoadItem(esp) for esp in listdir(path.join(self.config['Common']['Data'])) if esp.endswith(('.esm', '.esp', '.esl'))]

	def changeModInfo(self, item):
		iData = item.data(Qt.UserRole).split('|')
		name, ok = QInputDialog(self).getText(self, 'Edit', 'Name', QLineEdit.Normal, item.text())
		if ok:
			modId, ok = QInputDialog(self).getText(self, 'Edit', 'ID', QLineEdit.Normal, iData[0])
			if ok:
				version, ok = QInputDialog(self).getText(self, 'Edit', 'Version', QLineEdit.Normal, iData[1])
				if ok:
					rename(path.join(self.folder, 'mods', item.text()), path.join(self.folder, 'mods', name))
					item.setText(name)
					self.updateData(item, modId, version)

	def updateData(self, item, modId, version):
		item.setToolTip('ID: {}\nVersion: {}'.format(modId, version))
		item.setData(Qt.UserRole, '{}|{}'.format(modId, version))

	def addModItem(self, mod, check=Qt.Unchecked, modId='0', version='1.0'):
		if path.isdir(path.join(self.folder, 'mods', mod)):
			if not self.modList.findItems(mod, Qt.MatchExactly):
				modItem = QListWidgetItem(mod)
				modItem.setData(Qt.CheckStateRole, check)
				self.updateData(modItem, modId, version)
				self.modList.addItem(modItem)

	def addLoadItem(self, esp, check=Qt.Unchecked):
		if path.isfile(path.join(self.config['Common']['Data'], esp)):
			if not self.loadOrder.findItems(esp, Qt.MatchExactly):
				loadItem = QListWidgetItem(esp)
				loadItem.setData(Qt.CheckStateRole, check)
				self.loadOrder.addItem(loadItem)

	def selectSave(self):
		self.saveConfig()
		system('rm -rf "{}/"*'.format(self.config['Common']['Data']))
		[system('cp -as --remove-destination "{!s}/"* "{}"'.format(path.join(self.folder, 'mods', self.modList.item(index).text()), self.config['Common']['Data'])) for index in range(self.modList.count()) if self.modList.item(index).checkState()]
		self.refreshMods()

	def saveConfig(self):
		self.config['Mods'] = {x: '|'.join([self.modList.item(x).text(), str(self.modList.item(x).checkState()), self.modList.item(x).data(Qt.UserRole)]) for x in range(self.modList.count())}
		self.config['LoadOrder'] = {x: '|'.join([self.loadOrder.item(x).text(), str(self.loadOrder.item(x).checkState())]) for x in range(self.loadOrder.count())}
		with open(path.join(self.config['Common']['Plugins'], 'Plugins.txt'), 'w') as pFile:
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
		QMessageBox.information(self, 'Mod updates', 'Mod updates:\n' + updates, QMessageBox.Ok)

	def closeEvent(self, event):
		self.saveConfig()

if __name__ == '__main__':
	app = QApplication(argv)
	window = ModPlacer()
	exit(app.exec_())
