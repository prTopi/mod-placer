from os import makedirs, mkdir, rmdir, symlink, unlink, utime, walk
from os.path import isdir, islink, join
from shutil import move
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
        if self._config["Placer"].getboolean("emptyData"):
            self.cleanData(self._modConf["data"],
                          join(self._modConf["mods"], "Data Backup"))

        for mod in self._mods:
            self.copyTree(join(self._modConf["mods"], mod),
                          self._modConf["data"])

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

    def cleanData(self, srcTree, dstTree):
        for root, dirs, files in walk(srcTree, topdown=False):
            dstRoot = root.replace(srcTree, dstTree)
            for name in files:
                src = join(root, name)
                dst = join(dstRoot, name)
                try:
                    unlink(dst)
                except FileNotFoundError:
                    pass
                if not islink(src):
                    makedirs(dstRoot, exist_ok=True)
                    move(src, dst)
                else:
                    unlink(src)
            for name in dirs:
                rmdir(join(root, name))

    def copyTree(self, srcTree, dstTree):
        for root, dirs, files in walk(srcTree):
            dstRoot = root.replace(srcTree, dstTree)
            for name in dirs:
                dst = join(dstRoot, name)
                if not isdir(dst):
                    mkdir(dst)
            for name in files:
                src = join(root, name)
                dst = join(dstRoot, name)
                try:
                    unlink(dst)
                except FileNotFoundError:
                    pass
                symlink(src, dst)
