# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/options.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ConfigDialog(object):
    def setupUi(self, ConfigDialog):
        ConfigDialog.setObjectName("ConfigDialog")
        ConfigDialog.resize(400, 190)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ConfigDialog.sizePolicy().hasHeightForWidth())
        ConfigDialog.setSizePolicy(sizePolicy)
        ConfigDialog.setMaximumSize(QtCore.QSize(16777215, 190))
        self.verticalLayout = QtWidgets.QVBoxLayout(ConfigDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelApi = QtWidgets.QLabel(ConfigDialog)
        self.labelApi.setObjectName("labelApi")
        self.verticalLayout.addWidget(self.labelApi)
        self.lineEditApi = QtWidgets.QLineEdit(ConfigDialog)
        self.lineEditApi.setObjectName("lineEditApi")
        self.verticalLayout.addWidget(self.lineEditApi)
        self.labelConfig = QtWidgets.QLabel(ConfigDialog)
        self.labelConfig.setObjectName("labelConfig")
        self.verticalLayout.addWidget(self.labelConfig)
        self.horizontalLayoutButtons = QtWidgets.QHBoxLayout()
        self.horizontalLayoutButtons.setObjectName("horizontalLayoutButtons")
        self.comboBoxConfig = QtWidgets.QComboBox(ConfigDialog)
        self.comboBoxConfig.setObjectName("comboBoxConfig")
        self.horizontalLayoutButtons.addWidget(self.comboBoxConfig)
        self.pushButtonEdit = QtWidgets.QPushButton(ConfigDialog)
        self.pushButtonEdit.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButtonEdit.setObjectName("pushButtonEdit")
        self.horizontalLayoutButtons.addWidget(self.pushButtonEdit)
        self.toolButtonAdd = QtWidgets.QToolButton(ConfigDialog)
        self.toolButtonAdd.setObjectName("toolButtonAdd")
        self.horizontalLayoutButtons.addWidget(self.toolButtonAdd)
        self.verticalLayout.addLayout(self.horizontalLayoutButtons)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConfigDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ConfigDialog)
        QtCore.QMetaObject.connectSlotsByName(ConfigDialog)

    def retranslateUi(self, ConfigDialog):
        _translate = QtCore.QCoreApplication.translate
        ConfigDialog.setWindowTitle(_translate("ConfigDialog", "Options - Mod Placer"))
        self.labelApi.setText(_translate("ConfigDialog", "Api Key"))
        self.labelConfig.setText(_translate("ConfigDialog", "Config"))
        self.pushButtonEdit.setText(_translate("ConfigDialog", "Edit"))
        self.toolButtonAdd.setText(_translate("ConfigDialog", "+"))


