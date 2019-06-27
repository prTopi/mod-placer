# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/editmod.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EditModDialog(object):
    def setupUi(self, EditModDialog):
        EditModDialog.setObjectName("EditModDialog")
        EditModDialog.resize(400, 240)
        EditModDialog.setMaximumSize(QtCore.QSize(16777215, 240))
        EditModDialog.setModal(True)
        self.formLayout = QtWidgets.QFormLayout(EditModDialog)
        self.formLayout.setObjectName("formLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(EditModDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.nameLineEdit = QtWidgets.QLineEdit(EditModDialog)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.nameLabel = QtWidgets.QLabel(EditModDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.versionLineEdit = QtWidgets.QLineEdit(EditModDialog)
        self.versionLineEdit.setObjectName("versionLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.versionLineEdit)
        self.versionLabel = QtWidgets.QLabel(EditModDialog)
        self.versionLabel.setObjectName("versionLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.versionLabel)
        self.idLineEdit = QtWidgets.QLineEdit(EditModDialog)
        self.idLineEdit.setObjectName("idLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.idLineEdit)
        self.idLabel = QtWidgets.QLabel(EditModDialog)
        self.idLabel.setObjectName("idLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.idLabel)
        self.gameLineEdit = QtWidgets.QLineEdit(EditModDialog)
        self.gameLineEdit.setObjectName("gameLineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.gameLineEdit)
        self.gameLabel = QtWidgets.QLabel(EditModDialog)
        self.gameLabel.setObjectName("gameLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.gameLabel)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(4, QtWidgets.QFormLayout.FieldRole, spacerItem)
        self.nameLabel.setBuddy(self.nameLineEdit)

        self.retranslateUi(EditModDialog)
        self.buttonBox.accepted.connect(EditModDialog.accept)
        self.buttonBox.rejected.connect(EditModDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EditModDialog)

    def retranslateUi(self, EditModDialog):
        _translate = QtCore.QCoreApplication.translate
        EditModDialog.setWindowTitle(_translate("EditModDialog", "Edit mod - Mod Placer"))
        self.nameLabel.setText(_translate("EditModDialog", "Mod name"))
        self.versionLabel.setText(_translate("EditModDialog", "Version"))
        self.idLabel.setText(_translate("EditModDialog", "Nexus ID"))
        self.gameLabel.setText(_translate("EditModDialog", "Nexus game"))


