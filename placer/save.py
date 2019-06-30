from os import makedirs, listdir, symlink, unlink, rmdir, utime
from os.path import dirname, isdir, isfile, islink, join
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
                      join(self._config["mods"], "Data Backup"),
                      rm=False)
        for mod in self._mods:
            self.copyTree(join(self._config["mods"], mod),
                          self._config["data"])
        newTime = 978300000
        for file in listdir(self._config["data"]):
            if file.endswith(".bsa"):
                try:
                    utime(join(self._config["data"], file),
                        (newTime, newTime))
                except FileNotFoundError:
                    pass
        for plugin in self._plugins:
            try:
                utime(join(self._config["data"], plugin), (newTime, newTime))
                newTime += 1
            except FileNotFoundError:
                pass
        if self._config["plugins"]:
            makedirs(dirname(self._config["plugins"]), exist_ok=True)
            with open(join(self._config["plugins"]), "w") as f:
                for plugin in self._plugins:
                    if self._plugins[plugin]:
                        f.write(f"{self._config['prefix']}{plugin}\n")

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
