from json import load
from threading import Thread
from urllib.request import urlopen, Request
from PyQt5.QtCore import QThread, pyqtSignal


class UpdateThread(QThread):
    signalFinished = pyqtSignal(str)

    def __init__(self, mods, game, headers, parent):
        super().__init__(parent)
        self._mods = mods
        self._game = game
        self._headers = headers
        self._updates = ""

    def run(self):
        threads = [Thread(target=self.fetchInfo, args=(mod,))
                   for mod in self._mods]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        if not self._updates:
            self._updates = "No mod updates found."
        self.signalFinished.emit(self._updates)

    def fetchInfo(self, mod):
        if mod["id"] == "":
            return
        modID = mod["id"].split("/")
        if len(modID) == 1:
            modID.append(self._game)
        site = f"{modID[1]}/mods/{modID[0]}"
        try:
            req = Request("https://api.nexusmods.com/v1/games/"
                          f"{site}.json", headers=self._headers)
            with urlopen(req) as page:
                newVersion = load(page)["version"]
            if mod["version"] != newVersion:
                self._updates += "<a href=https://www.nexusmods.com/" \
                    f"{site}?tab=files>{mod['name']}: " \
                    f"{mod['version']} --> {newVersion}</a><br>"
        except Exception:
            self._updates += "<p>Failed opening nexus site for: " \
                f"{mod['name']}</p><br>"
