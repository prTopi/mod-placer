from os import chdir, listdir, mkdir, rmdir, unlink, walk
from os.path import basename, dirname, isdir, isfile, join, splitext
from re import search, sub
from shutil import move
from json import load
from urllib.request import urlopen, Request
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from placer import __basedir__
from placer.ui.installermanual import Ui_InstallerManualDialog


class InstallWorker(QObject):
    installError = pyqtSignal(str, str)
    installer = pyqtSignal(str, dict, int, dict)
    installFinished = pyqtSignal(str, dict)

    def __init__(self, config, headers, target):
        super().__init__()
        self._config = config
        self._target = target
        self._headers = headers
        self._temp = TemporaryDirectory()

    def prepare(self):
        try:
            from libarchive import extract_file, ArchiveError
        except ImportError as e:
            self.installError.emit("Import error", e.message)
            self._temp.cleanup()
            self.installFinished.emit("", {})
            return

        name = splitext(basename(self._target))[0]
        data = {"version": "", "id": ""}

        chdir(self._temp.name)
        try:
            extract_file(self._target)
        except ArchiveError as e:
            self.installError.emit("Error extracting archive", e.msg)
            self._temp.cleanup()
            self.installFinished.emit("", {})
            return
        self.normalizeTree(self._temp.name)

        try:
            nexusInfo = search(r"-(\d+)(.+)?$", name)
            name = sub(r"-(\d+)(.+)?$", "", name)
            data["id"] = nexusInfo[1]
            data["version"] = nexusInfo[2].replace("-", ".")[1:]
        except IndexError:
            pass

        if self._headers and data["id"]:
            try:
                url = "https://api.nexusmods.com/v1/games/" \
                    f"{self._config['game']}/mods/{data['id']}.json"
                req = Request(url, headers=self._headers)
                with urlopen(req) as site:
                    page = load(site)
                name = page["name"]
                data["version"] = page["version"]
            except Exception:
                pass

        installer = 0
        files = {}

        self.installer.emit(name, data, installer, files)

    @pyqtSlot(str, dict, dict)
    def complete(self, name, data, files):
        if name:
            self.moveTree(self._temp.name, join(self._config["mods"], name))

        chdir(__basedir__)
        self._temp.cleanup()
        self.installFinished.emit(name, data)

    def normalizeTree(self, folder, subDir=False):
        for root, dirs, files in walk(folder):
            for name in dirs:
                self.normalizeTree(join(root, name), True)

            for name in files:
                lowName = name.lower()
                if lowName != name:
                    if not lowName.endswith((".bsa", ".esm", ".esp", ".esl")):
                        move(join(folder, name), join(folder, lowName))

        if subDir:
            move(folder, join(dirname(folder), basename(folder).lower()))

    def moveTree(self, srcFolder, dstFolder, subDir=False):
        if not isdir(dstFolder):
            mkdir(dstFolder)

        for root, dirs, files in walk(srcFolder):
            for name in dirs:
                self.moveTree(join(root, name), join(dstFolder, name), True)

            for name in files:
                source = join(root, name)
                destination = join(dstFolder, name)
                move(source, destination)

        if subDir:
            rmdir(srcFolder)


class InstallerManualDialog(QDialog):
    def __init__(self, name, files, modConf, parent):
        super().__init__(parent)
        self._name = name
        self._files = files
        self._modConf = modConf
        self.Ui = Ui_InstallerManualDialog()
        self.Ui.setupUi(self)
        self.Ui.nameLineEdit.setText(name)
        self.show()

    def accept(self):
        name = self.Ui.nameLineEdit.text()
        if name in listdir(self._modConf["mods"]):
            msg = "Mod with that name already exists.\n" \
                "Do you want to merge these files?"
            cont = QMessageBox.warning(self, "Mod already exists", msg,
                                        QMessageBox.Yes | QMessageBox.No)
            if cont == QMessageBox.No:
                return
        super().accept()

    def getData(self):
        self._name = self.Ui.nameLineEdit.text()
        return self._name, self._files
