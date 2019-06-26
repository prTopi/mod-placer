from os import path, makedirs, listdir, symlink, unlink, rmdir
from shutil import copy2
from PyQt5.QtCore import QThread


class CommitThread(QThread):
    def __init__(self, dataDir, modsDir, mods, parent):
        super().__init__(parent)
        self._dataDir = dataDir
        self._modsDir = modsDir
        self._mods = mods

    def run(self):
        self.copyTree(self._dataDir, path.join(self._modsDir, "Data Backup"),
                      rm=False)
        for mod in self._mods:
            self.copyTree(path.join(self._modsDir, mod), self._dataDir)

    def copyTree(self, srcFolder, dstFolder, rm=None):
        for item in listdir(srcFolder):
            source = path.join(srcFolder, item)
            destination = path.join(dstFolder, item)
            if path.isdir(source):
                if rm is None:
                    if not path.isdir(destination):
                        makedirs(destination)
                    self.copyTree(source, destination)
                else:
                    self.copyTree(source, destination, rm=True)
            else:
                if path.islink(destination):
                    unlink(destination)
                if rm is None:
                    symlink(source, destination)
                else:
                    if path.isfile(source) and not path.islink(source):
                        makedirs(path.dirname(destination), exist_ok=True)
                        copy2(source, destination)
                    unlink(source)
        if rm:
            rmdir(srcFolder)
