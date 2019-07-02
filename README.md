# mod-placer
Script/program to manage mods of Bethesda games.

Made generally for Linux, not tested on anything else. Should work on everything, though on other systems, other programs most likely far surpass this one.

## Current features
- Basic mod installer (currently only takes archive, extract it and converts all file names to lower case)
- Able to set mod and load order
- Check for mod updates through Nexusmods (Needs own API key)
- Profile support

## Future plans
- Expand mod installer class:
  - Support FOMOD and BASH (and maybe OMOD)
  - Autoselect `data` folder if it's not the base folder
  - File/folder view, with ability to unselect undesired files
  - Add ability to use system program to extract archive if libarchive fails
- Check for updates from other sites? (LL)

## Game support
#### Tested
- TES V: Skyrim Special Edition
- TES V: Skyrim
- TES IV: Oblivion

#### Should work, untested
- Fallout 4
- Fallout 3, New Vegas

## Requirements
- [Python < 3.6](https://www.python.org/downloads/)
- [PyQt5](https://pypi.org/project/PyQt5/)
- [libarchive-c](https://pypi.org/project/libarchive-c/) - Optional, but needed to extract archives. If not on Linux system, refer to the GitHub README.md and read through issues to get running.
