# HL-Paker
Make .pak files for Half-Life 1 for use with Lambda1VR!

## Wizard usage
- Install HL (+ Blueshift and Opposing Force if desired) via steam or CD (haven't tested, but if you install to the default directory it should work). 
- If on Mac, open sidequest and allow your headset to connect to your computer (not necessary for windows)
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
```