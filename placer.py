#!/bin/python
import os, sys
pluginsFile = '/home/topi/Games/Steam/steamapps/compatdata/72850/pfx/drive_c/users/steamuser/Local Settings/Application Data/Skyrim/plugins.txt'
data = '/home/topi/Games/Steam/steamapps/common/Skyrim/Data/'
folders = sorted(os.listdir('Mods'))
mods = ','.join(sys.argv[1:])
if mods.strip():
	mods = [x.split('-') for x in mods.split(',')]
	mods = [str(y) for x in mods for y in range(int(x[0]), int(x[-1])+1)]
	mods = [x if len(x) > 1 else '0'+x for x in mods]
else:
	mods = [x[:2] for x in folders]
os.system('rm -rf "{}*"'.format(data))
[os.system('cp -as --remove-destination "{!s}/Mods/{!s}-*/*" "{}"'.format(os.path.dirname(os.path.realpath(__file__)), x, data)) for x in mods]
files = os.listdir(data)
with open(pluginsFile) as f:
	plugins = f.read().splitlines()
	files = [x for x in files if '.esp' in x or '.esm' in x]
	newfiles = [x for x in files if x not in set(plugins)]
with open(pluginsFile, 'w') as f:
	[f.write(x+'\n') for x in plugins if x in set(files)]
	if newfiles:
		f.write('\n\n#NEW STUFF\n')
		[f.write(x+'\n') for x in newfiles]
		os.system('kate "{}"'.format(pluginsFile))
