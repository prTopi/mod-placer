from os import getcwd, chdir, listdir, makedirs, rmdir, rename, unlink
from os.path import basename, dirname, isdir, isfile, join, splitext
from re import search, sub
from shutil import copy2, rmtree
from json import load
from urllib.request import urlopen, Request
from contextlib import contextmanager
from PyQt5.QtCore import QThread, pyqtSignal


class InstallThread(QThread):
    installError = pyqtSignal(str, str)
    finishInstall = pyqtSignal(str, dict)

    def __init__(self, config, headers, target, parent):
        super().__init__(parent)
        self._config = config
        self._target = target
        self._headers = headers

    @contextmanager
    def tmpdir(self):
        start = getcwd()
        if isdir(".tmp"):
            rmtree(".tmp")
        makedirs(".tmp")
        chdir(".tmp")
        try:
            yield
        finally:
            if isdir(".tmp"):
                rmtree(".tmp")
            chdir(start)

    def run(self):
        try:
            from libarchive import extract_fd, ArchiveError
        except ImportError as e:
            installError.emit("Import error", e.message)
            self.finishInstall.emit("", {})
            return
        name = splitext(basename(self._target))[0]
        data = {"version": "", "id": ""}
        with self.tmpdir():
            try:
                with open(self._target, "r+b") as f:
                        extract_fd(f.fileno())
            except ArchiveError as e:
                self.installError.emit("Error extracting archive", e.msg)
                self.finishInstall.emit("", {})
                return
            self.normalizeTree(getcwd())
            try:
                nexusInfo = search("-(\d+)(.+)?$", name)
                name = sub("-(\d+)(.+)?$", "", name)
                data["id"] = nexusInfo[1]
                data["version"] = nexusInfo[2].replace("-", ".")[1:]
            except Exception:
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
            self.moveTree(getcwd(), join(self._config["mods"], name))
        self.finishInstall.emit(name, data)

    def normalizeTree(self, folder):
        for item in listdir(folder):
            source = join(folder, item)
            if isdir(source):
                self.normalizeTree(source)
            else:
                item = item.lower()
                if not item.endswith((".bsa", ".esm", ".esp", ".esl")):
                    rename(source, join(folder, item))
        rename(folder, join(dirname(folder), basename(folder).lower()))

    def moveTree(self, srcFolder, dstFolder):
        for item in listdir(srcFolder):
            source = join(srcFolder, item)
            destination = join(dstFolder, item)
            if isdir(source):
                self.moveTree(source, destination)
            else:
                if isfile(destination):
                    unlink(destination)
                makedirs(dirname(destination), exist_ok=True)
                copy2(source, destination)
                unlink(source)
        rmdir(srcFolder)
