# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/editconfig.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EditConfigDialog(object):
    def setupUi(self, EditConfigDialog):
        EditConfigDialog.setObjectName("EditConfigDialog")
        EditConfigDialog.resize(400, 300)
        EditConfigDialog.setMaximumSize(QtCore.QSize(16777215, 300))
        EditConfigDialog.setModal(True)
        self.formLayout_2 = QtWidgets.QFormLayout(EditConfigDialog)
        self.formLayout_2.setObjectName("formLayout_2")
        self.nameLabel = QtWidgets.QLabel(EditConfigDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(EditConfigDialog)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.gameLabel = QtWidgets.QLabel(EditConfigDialog)
        self.gameLabel.setObjectName("gameLabel")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.gameLabel)
        self.gameLineEdit = QtWidgets.QLineEdit(EditConfigDialog)
        self.gameLineEdit.setObjectName("gameLineEdit")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.gameLineEdit)
        self.dataLabel = QtWidgets.QLabel(EditConfigDialog)
        self.dataLabel.setObjectName("dataLabel")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.dataLabel)
        self.dataHorizontalLayout = QtWidgets.QHBoxLayout()
        self.dataHorizontalLayout.setObjectName("dataHorizontalLayout")
        self.dataLineEdit = QtWidgets.QLineEdit(EditConfigDialog)
        self.dataLineEdit.setObjectName("dataLineEdit")
        self.dataHorizontalLayout.addWidget(self.dataLineEdit)
        self.dataToolButton = QtWidgets.QToolButton(EditConfigDialog)
        self.dataToolButton.setObjectName("dataToolButton")
        self.dataHorizontalLayout.addWidget(self.dataToolButton)
        self.formLayout_2.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.dataHorizontalLayout)
        self.modsLabel = QtWidgets.QLabel(EditConfigDialog)
        self.modsLabel.setObjectName("modsLabel")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.modsLabel)
        self.modsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.modsHorizontalLayout.setObjectName("modsHorizontalLayout")
        self.modsLineEdit = QtWidgets.QLineEdit(EditConfigDialog)
        self.modsLineEdit.setObjectName("modsLineEdit")
        self.modsHorizontalLayout.addWidget(self.modsLineEdit)
        self.modsToolButton = QtWidgets.QToolButton(EditConfigDialog)
        self.modsToolButton.setObjectName("modsToolButton")
        self.modsHorizontalLayout.addWidget(self.modsToolButton)
        self.formLayout_2.setLayout(4, QtWidgets.QFormLayout.FieldRole, self.modsHorizontalLayout)
        self.pluginsLabel = QtWidgets.QLabel(EditConfigDialog)
        self.pluginsLabel.setObjectName("pluginsLabel")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.pluginsLabel)
        self.pluginsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.pluginsHorizontalLayout.setObjectName("pluginsHorizontalLayout")
        self.pluginsLineEdit = QtWidgets.QLineEdit(EditConfigDialog)
        self.pluginsLineEdit.setObjectName("pluginsLineEdit")
        self.pluginsHorizontalLayout.addWidget(self.pluginsLineEdit)
        self.pluginsToolButton = QtWidgets.QToolButton(EditConfigDialog)
        self.pluginsToolButton.setObjectName("pluginsToolButton")
        self.pluginsHorizontalLayout.addWidget(self.pluginsToolButton)
        self.formLayout_2.setLayout(5, QtWidgets.QFormLayout.FieldRole, self.pluginsHorizontalLayout)
        self.prefixLabel = QtWidgets.QLabel(EditConfigDialog)
        self.prefixLabel.setObjectName("prefixLabel")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.prefixLabel)
        self.prefixLineEdit = QtWidgets.QLineEdit(EditConfigDialog)
        self.prefixLineEdit.setObjectName("prefixLineEdit")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.prefixLineEdit)
        self.buttonBox = QtWidgets.QDialogButtonBox(EditConfigDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout_2.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout_2.setItem(7, QtWidgets.QFormLayout.FieldRole, spacerItem)
        self.nameLabel.setBuddy(self.nameLineEdit)
        self.gameLabel.setBuddy(self.gameLineEdit)
        self.dataLabel.setBuddy(self.dataLineEdit)
        self.modsLabel.setBuddy(self.modsLineEdit)
        self.pluginsLabel.setBuddy(self.pluginsLineEdit)
        self.prefixLabel.setBuddy(self.prefixLineEdit)

        self.retranslateUi(EditConfigDialog)
        self.buttonBox.accepted.connect(EditConfigDialog.accept)
        self.buttonBox.rejected.connect(EditConfigDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EditConfigDialog)

    def retranslateUi(self, EditConfigDialog):
        _translate = QtCore.QCoreApplication.translate
        EditConfigDialog.setWindowTitle(_translate("EditConfigDialog", "Edit Config - Mod Placer"))
        self.nameLabel.setText(_translate("EditConfigDialog", "Name"))
        self.gameLabel.setText(_translate("EditConfigDialog", "Nexus game"))
        self.dataLabel.setText(_translate("EditConfigDialog", "Data directory"))
        self.dataToolButton.setText(_translate("EditConfigDialog", "..."))
        self.modsLabel.setText(_translate("EditConfigDialog", "Mods directory"))
        self.modsToolButton.setText(_translate("EditConfigDialog", "..."))
        self.pluginsLabel.setText(_translate("EditConfigDialog", "Plugins file"))
        self.pluginsToolButton.setText(_translate("EditConfigDialog", "..."))
        self.prefixLabel.setText(_translate("EditConfigDialog", "Plugins line prefix"))


