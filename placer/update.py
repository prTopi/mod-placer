from json import load
from urllib.request import urlopen, Request
from PyQt5.QtCore import QThread


class UpdateThread(QThread):
    def __init__(self, mods, game, headers, parent):
        super().__init__(parent)
        self._mods = mods
        self._game = game
        self._headers = headers
        self._updates = ""

    def run(self):
        for mod in self._mods:
            modNexus = mod["id"]
            modVersion = mod["version"]
            if modNexus != "":
                modID = modNexus.split("/")
                if len(modID) == 1:
                    modID.append(self._game)
                site = f"{modID[1]}/mods/{modID[0]}"
                try:
                    req = Request("https://api.nexusmods.com/v1/games/"
                                  f"{site}.json", headers=self._headers)
                    with urlopen(req) as page:
                        newVersion = load(page)["version"]
                    if modVersion != newVersion:
                        self._updates += "<a href=https://www.nexusmods.com/" \
                            f"{site}?tab=files>{mod['name']}: {modVersion} " \
                            f"--> {newVersion}</a><br>"
                except Exception:
                    self._updates += "<p>Failed opening nexus site for: " \
                        f"{mod['name']}</p><br>"
        if not self._updates:
            self._updates = "No mod updates found."

    def getUpdates(self):
        return self._updates
