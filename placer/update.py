from json import load
from threading import Thread
from urllib.request import urlopen, Request
from PyQt5.QtCore import Qt, QObject, pyqtSignal


class UpdateWorker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, mods, game, headers):
        super().__init__()
        self._mods = mods
        self._game = game
        self._headers = headers
        self._updates = ""

    def fetchUpdates(self):
        threads = [Thread(target=self.fetchInfo, args=(mod,))
                   for mod in self._mods]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        if not self._updates:
            self._updates = "No mod updates found."
        self.finished.emit(self._updates)

    def fetchInfo(self, mod):
        if mod.data(Qt.UserRole + 2) == "":
            return
        modID = mod.data(Qt.UserRole + 2).split("|")
        if len(modID) == 1:
            modID.append(self._game)
        site = f"{modID[1]}/mods/{modID[0]}"
        try:
            req = Request("https://api.nexusmods.com/v1/games/"
                          f"{site}.json", headers=self._headers)
            with urlopen(req) as page:
                newVersion = load(page)["version"]
            if mod.data(Qt.UserRole + 1) != newVersion:
                self._updates += "<a href=https://www.nexusmods.com/" \
                    f"{site}?tab=files>{mod.data(Qt.UserRole)}: " \
                    f"{mod.data(Qt.UserRole + 1)} --> {newVersion}</a><br>"
        except Exception:
            self._updates += "<p>Failed opening nexus site for: " \
                f"{mod.data(Qt.UserRole)}</p><br>"
