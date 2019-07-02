from os import chdir, mkdir, rmdir, unlink, walk
from os.path import basename, dirname, isdir, isfile, join, splitext
from re import search, sub
from shutil import move
from json import load
from urllib.request import urlopen, Request
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from PyQt5.QtCore import QObject, pyqtSignal
from placer import __basedir__


class InstallWorker(QObject):
    installError = pyqtSignal(str, str)
    finished = pyqtSignal(str, dict)

    def __init__(self, config, headers, target):
        super().__init__()
        self._config = config
        self._target = target
        self._headers = headers

    def install(self):
        try:
            from libarchive import extract_file, ArchiveError
        except ImportError as e:
            self.installError.emit("Import error", e.message)
            self.finished.emit("", {})
            return

        name = splitext(basename(self._target))[0]
        data = {"version": "", "id": ""}

        with TemporaryDirectory() as root:
            chdir(root)
            try:
                extract_file(self._target)
            except ArchiveError as e:
                self.installError.emit("Error extracting archive", e.msg)
                self.finished.emit("", {})
                return
            self.normalizeTree(root)

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

            self.moveTree(root, join(self._config["mods"], name))
            chdir(__basedir__)
        self.finished.emit(name, data)

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
