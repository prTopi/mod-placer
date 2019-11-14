from os import chdir, chmod, listdir, mkdir, walk
from os.path import basename, isdir, join, splitext
from re import search, sub
from shutil import move
from json import load
from urllib.request import urlopen, Request
from tempfile import TemporaryDirectory
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
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
            self.installError.emit("Import error", str(e))
            self._temp.cleanup()
            self.installFinished.emit("", {})
            return
        name = splitext(basename(self._target))[0]
        data = {"version": "", "source": "Nexus", "id": "", "game": ""}
        chdir(self._temp.name)
        try:
            extract_file(self._target)
        except ArchiveError as e:
            self.installError.emit("Error extracting archive", e.msg)
            self._temp.cleanup()
            self.installFinished.emit("", {})
            return
        files = self.normalizeTree(self._temp.name)
        try:
            nexusInfo = search(r"-(\d+)(.+)?$", name)
            name = sub(r"-(\d+)(.+)?$", "", name)
            data["id"] = nexusInfo[1]
            data["version"] = nexusInfo[2].replace("-", ".")[1:]
        except (AttributeError, IndexError, TypeError):
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
        elif not data["id"]:
            data["source"] = "Other"
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

    def normalizeTree(self, folder):
        for root, dirs, files in walk(folder):
            for name in dirs:
                src = join(root, name)
                chmod(src, 0o755)
        for root, dirs, files in walk(folder, topdown=False):
            for name in files:
                src = join(root, name)
                chmod(src, 0o644)
                lowName = name.lower()
                if lowName != name:
                    if not lowName.endswith((".bsa", ".esm", ".esp", ".esl")):
                        move(src, join(root, lowName))
            for name in dirs:
                src = join(root, name)
                move(src, join(root, name.lower()))

    def moveTree(self, srcTree, dstTree):
        if not isdir(dstTree):
            mkdir(dstTree)
        for root, dirs, files in walk(srcTree):
            dstRoot = root.replace(srcTree, dstTree)
            for name in dirs:
                dst = join(dstRoot, name)
                if not isdir(dst):
                    mkdir(dst)
            for name in files:
                if name != "desktop.ini" and name != "thumbs.db":
                    src = join(root, name)
                    dst = join(dstRoot, name)
                    move(src, dst)


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
