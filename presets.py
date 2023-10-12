from pathlib import Path


BASE_DIRS_TO_TRY = [
    'C:\Program Files (x86)\Steam\steamapps\common\Half-Life',
    'C:\Program Files\Steam\steamapps\common\Half-Life',
    'C:\Sierra\Half-Life',
    '~/Library/Application Support/Steam/steamapps/common/Half-Life',  # Mac
]

# Add D-Z to the list of directories to try if you have it installed
# Iterate through alphabet
for letter in range(ord('D'), ord('Z') + 1):
    BASE_DIRS_TO_TRY.append(f'{chr(letter)}:\Program Files (x86)\Steam\steamapps\common\Half-Life')
    BASE_DIRS_TO_TRY.append(f'{chr(letter)}:\Program Files\Steam\steamapps\common\Half-Life')
    BASE_DIRS_TO_TRY.append(f'{chr(letter)}:\Sierra\Half-Life')

LAMBDA1_APK_URL_QUEST = 'https://github.com/DrBeef/Lambda1VR/releases/download/v1.5.1/lambda1vr-v1.5.1.apk'
LAUNCHER_APK_URL_QUEST = 'https://github.com/berndolauerto/Lambda1VR_Launcher/releases/download/2.1/Lambda1_Launcher_Quest.apk'

APK_CONFIGS = {
    'quest': {
        'lambda1': {
            'apk_url': LAMBDA1_APK_URL_QUEST,
            'name': 'com.drbeef.lambda1vr',
        },
        'launcher': {
            'apk_url': LAUNCHER_APK_URL_QUEST,
            'name': 'com.CactusStudios.Lambda1VR_Launcher',
        }
    },
}

HL_GOLD_HD_URL = 'https://github.com/ryan-cranfill/hl-paker/releases/download/0.1.1/hl_gold_hd.zip'


def search_for_halflife(additional_dirs=None) -> Path:
    # Try to find the half-life directory
    for dir in BASE_DIRS_TO_TRY:
        p = Path(dir).expanduser()
        if p.exists():
            return p
        
    # If we didn't find it, try the additional directories if they were specified
    if additional_dirs:
        for dir in additional_dirs:
            p = Path(dir).expanduser()
        if p.exists():
            return p
    return 'Unable to find Half-Life directory.'


presets = {
    'hl_vanilla': {
        'base_folder': 'valve',
        'also_include_overwrites': None,
        'description': 'Vanilla Half-Life with no mods or texture packs.',
    },
    'hl_hd': {
        'base_folder': 'valve',
        'also_include_overwrites': ['valve_hd'],
        'description': 'Half-Life with the default HD texture pack.',
    },
    'hl_gold_hd': {
        'base_folder': 'HL_Gold_HD',
        'also_include_overwrites': None,
        'commandline': 'xash3d -log --supersampling 1.25 --msaa 2 --cpu 4 --gpu 4 -game HL_Gold_HD',
        'description': 'Half-Life with the Half-Life Gold HD pack. NOTE: Do this after you have installed hl_vanilla or hl_hd, as this pack does not include all of the base Half-Life files.',
    },
    'hl_ai_upscale': {
        'base_folder': 'valve',
        'also_include_overwrites': ['valve_hd', 'STEP 4/valve', 'STEP 5/valve'],  # Extract the AI upscaled textures to STEP 4 and STEP 5 folders in the HL directory
        'commandline': 'xash3d -log --supersampling 1.25 --msaa 2 --cpu 4 --gpu 4',
        'ignore_files': ['gameinfo.txt', 'config.cfg'],
        'description': 'Half-Life with the AI upscaled textures. NOTE: Before running this, you must copy the STEP 4 and STEP 5 folders from the AI upscale zip to "STEP 4" and "STEP 5" in the HL directory.',
    },
    'blueshift_vanilla': {
        'base_folder': 'bshift',
        'also_include_overwrites': None,
        'commandline': 'xash3d -log --supersampling 1.25 --msaa 2 --cpu 4 --gpu 4 -game bshift',
        'description': 'Half-Life: Blue Shift with no mods or texture packs.',
    },
    'blueshift_hd': {
        'base_folder': 'bshift',
        'also_include_overwrites': ['bshift_hd'],
        'commandline': 'xash3d -log --supersampling 1.25 --msaa 2 --cpu 4 --gpu 4 -game bshift',
        'description': 'Half-Life: Blue Shift with the default HD texture pack.',
    },
    'blueshift_ai_upscale': {
        'base_folder': 'bshift',
        'also_include_overwrites': ['bshift_hd', 'STEP 4\\blueshift_unlocked', 'STEP 5\\blueshift_unlocked'],  # Extract the AI upscaled textures to STEP 4 and STEP 5 folders in the HL directory
        'ignore_files': ['gameinfo.txt', 'config.cfg'],
        'commandline': 'xash3d -log --supersampling 1.25 --msaa 2 --cpu 4 --gpu 4 -game bshift',
        'description': 'Half-Life: Blue Shift with the AI upscaled textures. NOTE: Before running this, you must copy the STEP 4 and STEP 5 folders from the AI upscale zip to "STEP 4" and "STEP 5" in the HL directory.',
    },
    'opfor_vanilla': {
        'base_folder': 'gearbox',
        'also_include_overwrites': None,
        'commandline': 'xash3d -log --supersampling 1.25 --msaa 2 --cpu 4 --gpu 4 -game gearbox',
        'description': 'Half-Life: Opposing Force with no mods or texture packs.',
    },
    'opfor_hd': {
        'base_folder': 'gearbox',
        'also_include_overwrites': ['gearbox_hd'],
        'commandline': 'xash3d -log --supersampling 1.25 --msaa 2 --cpu 4 --gpu 4 -game gearbox',
        'description': 'Half-Life: Opposing Force with the default HD texture pack.',
    },
    'opfor_ai_upscale': {
        'base_folder': 'gearbox',
        'also_include_overwrites': ['gearbox_hd', 'STEP 4\\gearbox', 'STEP 5\\gearbox'],  # Extract the AI upscaled textures to STEP 4 and STEP 5 folders in the HL directory
        'ignore_files': ['gameinfo.txt', 'config.cfg'],
        'commandline': 'xash3d -log --supersampling 1.25 --msaa 2 --cpu 4 --gpu 4 -game gearbox',
        'description': 'Half-Life: Opposing Force with the AI upscaled textures. NOTE: Before running this, you must copy the STEP 4 and STEP 5 folders from the AI upscale zip to "STEP 4" and "STEP 5" in the HL directory.',
    },
}