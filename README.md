# McModPkg

McModPkg is a stupid simple Minecraft mod package manager.

It relies on a local index (`index.json`) that contains all the info on
versions, download links, dependencies, etc.
Naturally, if the index doesn't have a given mod, mcmodpkg can't download
it.

To use it to for instance download the Thermal Dynamics mod and all its
dependencies for Minecraft 1.11.2, run:
```
~$ ./mcmodpkg.py --mcversion 1.11.2 thermaldynamics
Resolving thermaldynamics..
Downloading https://minecraft.curseforge.com/projects/thermal-dynamics/files/2469620/download
Ignoring forge
Resolving cofhcore..
Downloading https://minecraft.curseforge.com/projects/cofhcore/files/2469613/download
Resolving thermalfoundation..
Downloading https://minecraft.curseforge.com/projects/thermal-foundation/files/2453220/download
```

All the mod jars are now downloaded into `./downloads/1.11.2/` which you
can move to you Minecraft mod folder.
Note that this of course assumes Forge.


To see a list of mods in the index, run:
```
~$ ./mcmodpkg.py --list
Baubles - Adding a touch of bling to Minecraft
...
```


## How to contribute

If you want to add a missing mod or fix incorrect package data, add it
to `index.json` and send a pull request.
