from os import path, makedirs, listdir, symlink, unlink, rmdir
from shutil import copy2
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot


class CommitThread(QThread):
    def __init__(self, dataDir, modsDir, mods, parent):
        super().__init__()
        self._dataDir = dataDir
        self._modsDir = modsDir
        self._mods = mods
        self._parent = parent

    def run(self):
        self.copyTree(self._dataDir, path.join(self._modsDir, "Data Backup"),
                      rm=True)
        makedirs(self._dataDir)
        for mod in self._mods:
            self.copyTree(path.join(self._modsDir, mod), self._dataDir)

    def copyTree(self, source, destination, rm=False):
        for item in listdir(source):
            src = path.join(source, item)
            dst = path.join(destination, item)
            if path.isdir(src):
                if not path.isdir(dst) and not rm:
                    makedirs(dst)
                self.copyTree(src, dst, rm)
            else:
                if path.islink(dst):
                    unlink(dst)
                if rm:
                    if path.isfile(src) and not path.islink(src):
                        makedirs(path.dirname(dst), exist_ok=True)
                        copy2(src, dst)
                    unlink(src)
                else:
                    symlink(src, dst)
        if rm:
            rmdir(source)
