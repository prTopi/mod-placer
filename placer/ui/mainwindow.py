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
        self.listsLayout = QtWidgets.QHBoxLayout()
        self.listsLayout.setObjectName("listsLayout")
        self.modsLayout = QtWidgets.QVBoxLayout()
        self.modsLayout.setObjectName("modsLayout")
        self.modLabel = QtWidgets.QLabel(self.centralwidget)
        self.modLabel.setObjectName("modLabel")
        self.modsLayout.addWidget(self.modLabel)
        self.modListWidget = QtWidgets.QListWidget(self.centralwidget)
        self.modListWidget.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.modListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.modListWidget.setObjectName("modListWidget")
        self.modsLayout.addWidget(self.modListWidget)
        self.listsLayout.addLayout(self.modsLayout)
        self.loadLayout = QtWidgets.QVBoxLayout()
        self.loadLayout.setObjectName("loadLayout")
        self.loadLabel = QtWidgets.QLabel(self.centralwidget)
        self.loadLabel.setObjectName("loadLabel")
        self.loadLayout.addWidget(self.loadLabel)
        self.loadListWidget = QtWidgets.QListWidget(self.centralwidget)
        self.loadListWidget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.loadListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.loadListWidget.setObjectName("loadListWidget")
        self.loadLayout.addWidget(self.loadListWidget)
        self.listsLayout.addLayout(self.loadLayout)
        self.verticalLayout.addLayout(self.listsLayout)
        self.layoutButtons = QtWidgets.QHBoxLayout()
        self.layoutButtons.setObjectName("layoutButtons")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layoutButtons.addItem(spacerItem)
        self.savePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.savePushButton.setEnabled(False)
        self.savePushButton.setObjectName("savePushButton")
        self.layoutButtons.addWidget(self.savePushButton)
        self.verticalLayout.addLayout(self.layoutButtons)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 28))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.actionRefresh = QtWidgets.QAction(MainWindow)
        self.actionRefresh.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.actionRefresh.setIcon(icon)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionCheckForUpdates = QtWidgets.QAction(MainWindow)
        self.actionCheckForUpdates.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.actionCheckForUpdates.setIcon(icon)
        self.actionCheckForUpdates.setObjectName("actionCheckForUpdates")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("application-exit")
        self.actionQuit.setIcon(icon)
        self.actionQuit.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionRefresh)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionCheckForUpdates)
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.actionQuit.triggered.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mod Placer"))
        self.modLabel.setText(_translate("MainWindow", "Mods"))
        self.loadLabel.setText(_translate("MainWindow", "Load Order"))
        self.savePushButton.setText(_translate("MainWindow", "Save"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionRefresh.setText(_translate("MainWindow", "Refresh"))
        self.actionRefresh.setShortcut(_translate("MainWindow", "F5"))
        self.actionCheckForUpdates.setText(_translate("MainWindow", "Check for Updates"))
        self.actionCheckForUpdates.setShortcut(_translate("MainWindow", "Ctrl+F5"))
        self.actionSettings.setText(_translate("MainWindow", "Configure..."))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q"))


