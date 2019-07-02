# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/editmod.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
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
        self.nameLabel = QtWidgets.QLabel(EditModDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(EditModDialog)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.versionLabel = QtWidgets.QLabel(EditModDialog)
        self.versionLabel.setObjectName("versionLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.versionLabel)
        self.versionLineEdit = QtWidgets.QLineEdit(EditModDialog)
        self.versionLineEdit.setObjectName("versionLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.versionLineEdit)
        self.sourceLabel = QtWidgets.QLabel(EditModDialog)
        self.sourceLabel.setObjectName("sourceLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.sourceLabel)
        self.sourceComboBox = QtWidgets.QComboBox(EditModDialog)
        self.sourceComboBox.setObjectName("sourceComboBox")
        self.sourceComboBox.addItem("")
        self.sourceComboBox.addItem("")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.sourceComboBox)
        self.dataOneLabel = QtWidgets.QLabel(EditModDialog)
        self.dataOneLabel.setObjectName("dataOneLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.dataOneLabel)
        self.dataOneLineEdit = QtWidgets.QLineEdit(EditModDialog)
        self.dataOneLineEdit.setObjectName("dataOneLineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.dataOneLineEdit)
        self.dataTwoLabel = QtWidgets.QLabel(EditModDialog)
        self.dataTwoLabel.setObjectName("dataTwoLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.dataTwoLabel)
        self.dataTwoLineEdit = QtWidgets.QLineEdit(EditModDialog)
        self.dataTwoLineEdit.setObjectName("dataTwoLineEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.dataTwoLineEdit)
        self.buttonBox = QtWidgets.QDialogButtonBox(EditModDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(5, QtWidgets.QFormLayout.FieldRole, spacerItem)
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
        self.sourceLabel.setText(_translate("EditModDialog", "Source"))
        self.sourceComboBox.setItemText(0, _translate("EditModDialog", "Nexus"))
        self.sourceComboBox.setItemText(1, _translate("EditModDialog", "Other"))
        self.dataOneLabel.setText(_translate("EditModDialog", "Nexus ID"))
        self.dataTwoLabel.setText(_translate("EditModDialog", "Nexus game"))
