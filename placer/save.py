from os import path, makedirs, listdir, symlink, unlink, rmdir, utime
from shutil import copy2
from PyQt5.QtCore import QThread


class SaveThread(QThread):
    def __init__(self, config, mods, plugins, parent):
        super().__init__(parent)
        self._config = config
        self._mods = mods
        self._plugins = plugins

    def run(self):
        self.copyTree(self._config["data"],
                      path.join(self._config["mods"], "Data Backup"),
                      rm=False)
        for mod in self._mods:
            self.copyTree(path.join(self._config["mods"], mod),
                          self._config["data"])
        newTime = 978300000
        for file in listdir(self._config["data"]):
            if file.endswith(".bsa"):
                utime(path.join(self._config["data"], file),
                      (newTime, newTime))
        for plugin in self._plugins:
            utime(path.join(self._config["data"], plugin), (newTime, newTime))
            newTime += 1
        if self._config["plugins"]:
            makedirs(path.dirname(self._config["plugins"]), exist_ok=True)
            with open(path.join(self._config["plugins"]), "w") as f:
                for plugin in self._plugins:
                    f.write(f"{self._config['prefix']}{plugin}\n")

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
