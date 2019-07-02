# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/installermanual.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_InstallerManualDialog(object):
    def setupUi(self, InstallerManualDialog):
        InstallerManualDialog.setObjectName("InstallerManualDialog")
        InstallerManualDialog.resize(500, 400)
        self.verticalLayout = QtWidgets.QVBoxLayout(InstallerManualDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.nameFormLayout = QtWidgets.QFormLayout()
        self.nameFormLayout.setObjectName("nameFormLayout")
        self.nameLabel = QtWidgets.QLabel(InstallerManualDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.nameFormLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(InstallerManualDialog)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameFormLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.verticalLayout.addLayout(self.nameFormLayout)
        self.treeWidget = QtWidgets.QTreeWidget(InstallerManualDialog)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.verticalLayout.addWidget(self.treeWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(InstallerManualDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(InstallerManualDialog)
        self.buttonBox.accepted.connect(InstallerManualDialog.accept)
        self.buttonBox.rejected.connect(InstallerManualDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(InstallerManualDialog)

    def retranslateUi(self, InstallerManualDialog):
        _translate = QtCore.QCoreApplication.translate
        InstallerManualDialog.setWindowTitle(_translate("InstallerManualDialog", "Dialog"))
        self.nameLabel.setText(_translate("InstallerManualDialog", "Name"))
