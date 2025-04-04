# HL-Paker
Make .pak files for Half-Life 1 for use with Lambda1VR!

## IMPORTANT NOTICE!
The HL 25th anniversary update has currently broken compatibility with Lambda1VR (as of 04/04/25). You'll need to downgrade your version of HL; [here is a video guide to doing so by Team Beef.](https://www.youtube.com/watch?v=DgAIruHRqTE)

## Wizard usage
- Install HL (+ Blueshift and Opposing Force if desired) via steam or CD (haven't tested, but if you install to the default directory it should work).
- If using the [AI upscale packs](https://www.moddb.com/mods/half-life-resrced-hd-graphics-mod/downloads/half-life-resrced-v10), extract the STEP 4 and STEP 5 folders into the base Half-Life directory (it should be at the same level as the `valve/` folder). **If you use these, you don't have to install the base HL/Opfor/BShift, as the AI upscale presets will do it for you.**
- Open sidequest and allow your headset to connect to your computer
- Run the wizard .exe, basically you click the buttons in order from top to bottom. IMPORTANT: WAIT for the popup telling you each step is complete before going on to the next one! It may not seem like it's doing anything but it probably is.
- **Reboot your headset!** Sometimes it gets a little funky for some reason but a reboot seems to work.
- Run the different games with the Cactus' launcher.
- **FOR EVERY DIFFERENT GAME**, make sure to enable materials in the configuration -> video menu on each game. There have been some crashes without doing that for some reason.
- Have fun!

## Requirements
- Python 3.6+

Before running, use `pip install -r requirements.txt`

## CLI version
Look at available presets with `python cli.py --show-presets`
```
python cli.py --preset <preset>
```

## Building
```
python -m PyInstaller gui.py --onefile --noconsole
python -m PyInstaller wizard_gui.py --onefile --add-data="platform-tools.zip;."
# For Mac:
python -m PyInstaller wizard_gui.py --onefile
```
