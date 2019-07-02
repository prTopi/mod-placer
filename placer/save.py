from os import makedirs, listdir, symlink, unlink, rmdir, utime
from os.path import dirname, isdir, isfile, islink, join
from shutil import copy2
from PyQt5.QtCore import QObject, pyqtSignal


class SaveThread(QObject):
    finished = pyqtSignal()

    def __init__(self, config, modConf, mods, plugins):
        super().__init__()
        self._config = config
        self._modConf = modConf
        self._mods = mods
        self._plugins = plugins

    def save(self):
        if self._config["Placer"].getboolean("emptyData"):
            self.copyTree(self._modConf["data"],
                          join(self._modConf["mods"], "Data Backup"),
                          rm=False)
        for mod in self._mods:
            self.copyTree(join(self._modConf["mods"], mod),
                          self._modConf["data"])
        newTime = 978300000
        for file in listdir(self._modConf["data"]):
            if file.lower().endswith(".bsa"):
                try:
                    utime(join(self._modConf["data"], file),
                          (newTime, newTime))
                except FileNotFoundError:
                    pass
        for plugin in self._plugins:
            try:
                utime(join(self._modConf["data"], plugin), (newTime, newTime))
                newTime += 1
            except FileNotFoundError:
                pass
        if self._modConf["plugins"]:
            makedirs(dirname(self._modConf["plugins"]), exist_ok=True)
            with open(join(self._modConf["plugins"]), "w") as f:
                for plugin in self._plugins:
                    if self._plugins[plugin]:
                        f.write(f"{self._modConf['prefix']}{plugin}\n")
        self.finished.emit()

    def copyTree(self, srcFolder, dstFolder, rm=None):
        for item in listdir(srcFolder):
            source = join(srcFolder, item)
            destination = join(dstFolder, item)
            if isdir(source):
                if rm is None:
                    if not isdir(destination):
                        makedirs(destination)
                    self.copyTree(source, destination)
                else:
                    self.copyTree(source, destination, rm=True)
            else:
                if islink(destination):
                    unlink(destination)
                if rm is None:
                    symlink(source, destination)
                else:
                    if isfile(source) and not islink(source):
                        makedirs(dirname(destination), exist_ok=True)
                        copy2(source, destination)
                    unlink(source)
        if rm:
            rmdir(srcFolder)
