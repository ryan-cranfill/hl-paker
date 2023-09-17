# HL-Paker
Make .pak files for Half-Life 1

## Requirements
- Python 3.6+

Before running, use `pip install -r requirements.txt`

## Usage
Look at available presets with `python cli.py --show-presets`
```
python cli.py --preset <preset>
```

## Building
```
python -m PyInstaller gui.py --onefile --noconsole
```