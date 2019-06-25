# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.layoutLists = QtWidgets.QHBoxLayout()
        self.layoutLists.setObjectName("layoutLists")
        self.layoutMods = QtWidgets.QVBoxLayout()
        self.layoutMods.setObjectName("layoutMods")
        self.labelMod = QtWidgets.QLabel(self.centralwidget)
        self.labelMod.setObjectName("labelMod")
        self.layoutMods.addWidget(self.labelMod)
        self.listWidgetMod = QtWidgets.QListWidget(self.centralwidget)
        self.listWidgetMod.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.listWidgetMod.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidgetMod.setObjectName("listWidgetMod")
        self.layoutMods.addWidget(self.listWidgetMod)
        self.layoutLists.addLayout(self.layoutMods)
        self.layoutLoad = QtWidgets.QVBoxLayout()
        self.layoutLoad.setObjectName("layoutLoad")
        self.labelLoad = QtWidgets.QLabel(self.centralwidget)
        self.labelLoad.setObjectName("labelLoad")
        self.layoutLoad.addWidget(self.labelLoad)
        self.listWidgetLoad = QtWidgets.QListWidget(self.centralwidget)
        self.listWidgetLoad.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.listWidgetLoad.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidgetLoad.setObjectName("listWidgetLoad")
        self.layoutLoad.addWidget(self.listWidgetLoad)
        self.layoutLists.addLayout(self.layoutLoad)
        self.verticalLayout.addLayout(self.layoutLists)
        self.layoutButtons = QtWidgets.QHBoxLayout()
        self.layoutButtons.setObjectName("layoutButtons")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layoutButtons.addItem(spacerItem)
        self.pushButtonSave = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonSave.setObjectName("pushButtonSave")
        self.layoutButtons.addWidget(self.pushButtonSave)
        self.verticalLayout.addLayout(self.layoutButtons)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 28))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.actionRefresh = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.actionRefresh.setIcon(icon)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionCheckForUpdates = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.actionCheckForUpdates.setIcon(icon)
        self.actionCheckForUpdates.setObjectName("actionCheckForUpdates")
        self.actionOptions = QtWidgets.QAction(MainWindow)
        self.actionOptions.setObjectName("actionOptions")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("application-exit")
        self.actionQuit.setIcon(icon)
        self.actionQuit.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionRefresh)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionCheckForUpdates)
        self.menuFile.addAction(self.actionOptions)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mod Placer"))
        self.labelMod.setText(_translate("MainWindow", "Mods"))
        self.labelLoad.setText(_translate("MainWindow", "Load Order"))
        self.pushButtonSave.setText(_translate("MainWindow", "Save"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionRefresh.setText(_translate("MainWindow", "Refresh"))
        self.actionRefresh.setShortcut(_translate("MainWindow", "F5"))
        self.actionCheckForUpdates.setText(_translate("MainWindow", "Check for Updates"))
        self.actionCheckForUpdates.setShortcut(_translate("MainWindow", "Ctrl+F5"))
        self.actionOptions.setText(_translate("MainWindow", "Configure..."))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q"))


