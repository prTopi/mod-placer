from os import makedirs, mkdir, rename, rmdir, symlink, unlink, utime, walk
from os.path import isdir, islink, join
from PyQt5.QtCore import QObject, pyqtSignal


class SaveWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, config, modConf, mods, plugins):
        super().__init__()
        self._config = config
        self._modConf = modConf
        self._mods = mods
        self._plugins = plugins

    def save(self):
        if self._config["Compatibility"].getboolean("useMove"):
            from shutil import move
            moveFunc = move
        else:
            moveFunc = rename

        if self._config["Placer"].getboolean("emptyData"):
            self.copyTree(self._modConf["data"],
                          join(self._modConf["mods"], "Data Backup"),
                          moveFunc, clean=True)

        for mod in self._mods:
            self.copyTree(join(self._modConf["mods"], mod),
                          self._modConf["data"], symlink)

        newTime = 946677600
        for root, dirs, files in walk(self._modConf["data"]):
            for name in files:
                if name.lower().endswith(".bsa"):
                    try:
                        utime(join(root, name), (newTime, newTime))
                    except FileNotFoundError:
                        pass

        for plugin in self._plugins:
            try:
                utime(join(self._modConf["data"], plugin), (newTime, newTime))
                newTime += 1
            except FileNotFoundError:
                pass

        if self._modConf["plugins"]:
            with open(join(self._modConf["plugins"]), "w") as f:
                for plugin in self._plugins:
                    if self._plugins[plugin]:
                        f.write(f"{self._modConf['prefix']}{plugin}\n")

        self.finished.emit()

    def copyTree(self, srcFolder, dstFolder, function, clean=False):
        if not clean:
            if not isdir(dstFolder):
                mkdir(dstFolder)
        for root, dirs, files in walk(srcFolder):
            for name in dirs:
                self.copyTree(join(root, name), join(dstFolder, name),
                              function, clean)
            for name in files:
                source = join(root, name)
                destination = join(dstFolder, name)
                try:
                    unlink(destination)
                except FileNotFoundError:
                    pass
                if not islink(source):
                    if clean:
                        makedirs(dstFolder, exist_ok=True)
                    function(source, destination)
                elif clean:
                    unlink(source)
        if clean:
            rmdir(srcFolder)
