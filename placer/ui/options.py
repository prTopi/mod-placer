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
        ConfigDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConfigDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.exitLabel = QtWidgets.QLabel(ConfigDialog)
        self.exitLabel.setObjectName("exitLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.exitLabel)
        self.exitCheckBox = QtWidgets.QCheckBox(ConfigDialog)
        self.exitCheckBox.setObjectName("exitCheckBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.exitCheckBox)
        self.focusLabel = QtWidgets.QLabel(ConfigDialog)
        self.focusLabel.setObjectName("focusLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.focusLabel)
        self.focusCheckBox = QtWidgets.QCheckBox(ConfigDialog)
        self.focusCheckBox.setObjectName("focusCheckBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.focusCheckBox)
        self.apiLabel = QtWidgets.QLabel(ConfigDialog)
        self.apiLabel.setObjectName("apiLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.apiLabel)
        self.apiLineEdit = QtWidgets.QLineEdit(ConfigDialog)
        self.apiLineEdit.setObjectName("apiLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.apiLineEdit)
        self.configLabel = QtWidgets.QLabel(ConfigDialog)
        self.configLabel.setObjectName("configLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.configLabel)
        self.buttonsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.buttonsHorizontalLayout.setObjectName("buttonsHorizontalLayout")
        self.configComboBox = QtWidgets.QComboBox(ConfigDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.configComboBox.sizePolicy().hasHeightForWidth())
        self.configComboBox.setSizePolicy(sizePolicy)
        self.configComboBox.setObjectName("configComboBox")
        self.buttonsHorizontalLayout.addWidget(self.configComboBox)
        self.editPushButton = QtWidgets.QPushButton(ConfigDialog)
        self.editPushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.editPushButton.setObjectName("editPushButton")
        self.buttonsHorizontalLayout.addWidget(self.editPushButton)
        self.addToolButton = QtWidgets.QToolButton(ConfigDialog)
        self.addToolButton.setObjectName("addToolButton")
        self.buttonsHorizontalLayout.addWidget(self.addToolButton)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.buttonsHorizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConfigDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.exitLabel.setBuddy(self.exitCheckBox)
        self.focusLabel.setBuddy(self.focusCheckBox)
        self.apiLabel.setBuddy(self.apiLineEdit)
        self.configLabel.setBuddy(self.configComboBox)

        self.retranslateUi(ConfigDialog)
        self.buttonBox.accepted.connect(ConfigDialog.accept)
        self.buttonBox.rejected.connect(ConfigDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConfigDialog)

    def retranslateUi(self, ConfigDialog):
        _translate = QtCore.QCoreApplication.translate
        ConfigDialog.setWindowTitle(_translate("ConfigDialog", "Options - Mod Placer"))
        self.exitLabel.setText(_translate("ConfigDialog", "Save on exit"))
        self.focusLabel.setText(_translate("ConfigDialog", "Refresh on focus"))
        self.apiLabel.setText(_translate("ConfigDialog", "Api Key"))
        self.configLabel.setText(_translate("ConfigDialog", "Config"))
        self.editPushButton.setText(_translate("ConfigDialog", "Edit"))
        self.addToolButton.setText(_translate("ConfigDialog", "+"))


