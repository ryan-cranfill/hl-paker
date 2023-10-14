from pathlib import Path
from ppadb.device import Device
from pak_util import make_hl_pak

from presets import presets, search_for_halflife, APK_CONFIGS
from adb_util import find_quest_devices, install_apk, make_folder, push_folder, check_if_app_installed, install_hl_gold_hd, copy_all_files


def install_lambda_and_launcher(quest_devices: list[Device], force_install: bool = False):
    # Install the APKs for the launcher and the game
    for apk_data in APK_CONFIGS['quest'].values():
        apk_url = apk_data['apk_url']
        app_name = apk_data['name']

        for device in quest_devices:
            device_name = device.get_properties()['ro.product.model']
            # Check if the app is already installed
            if check_if_app_installed(device, app_name) and not force_install:
                print(f'{app_name} is already installed on {device_name}, skipping.')
            else:
                print(f'Installing {apk_url} to {device_name}...')
                install_apk(apk_url, device)

def make_xash_folder(quest_devices: list[Device]):
    # Make the /xash/ folder on the device(s) if it doesn't exist
    print('Making /sdcard/xash/ folder on device(s)...')
    for device in quest_devices:
        make_folder(device, Path('/sdcard/xash/'))

def download_and_install_hl_gold(base_path: Path, zip_path: Path = None, force_install: bool = False):
    # Install the HL_Gold_HD pack if it's not already installed
    # Check if the folder exists locally
    hl_gold_hd_folder = base_path / 'HL_Gold_HD'
    if not hl_gold_hd_folder.exists() or force_install:
        print('Installing HL_Gold_HD...')
        install_hl_gold_hd(base_path, zip_path)
        # Ensure that the folder exists now
        if not hl_gold_hd_folder.exists():
            print(f'Error: HL_Gold_HD folder {hl_gold_hd_folder} does not exist.')
            exit(1)
    else:
        print(f'HL_Gold_HD folder {hl_gold_hd_folder} already exists, skipping.')

def pack_and_copy_hl_gold(quest_devices: list[Device], base_path: Path):
    hl_gold_hd_folder = base_path / 'HL_Gold_HD'
    # Pack the HL_Gold_HD folder and push it to the device(s)
    out_path = base_path / 'xash' / 'HL_Gold_HD'
    make_hl_pak(hl_gold_hd_folder, out_path, use_tqdm=True)
    remote_folder = Path('/sdcard/xash') / 'HL_Gold_HD'
    print(f'Pushing {out_path} to device(s) at {remote_folder}')
    for device in quest_devices:
        push_folder(device, out_path, remote_folder)
        # copy_all_files(device, out_path, remote_folder)

def pack_and_copy_preset(quest_devices: list[Device], base_path: Path, preset: str = 'hl_hd'):
    # Do the preset, then copy the output to the device(s)
    preset = presets[preset]
    base_path = base_path or Path(search_for_halflife())
    game_path = base_path / preset['base_folder']
    if not game_path.exists():
        print(f'Error: Game path {game_path} does not exist.')
    else:
        also_include = [base_path / new_folder for new_folder in preset['also_include_overwrites']] if preset['also_include_overwrites'] else []
        out_path = base_path / 'xash' / preset['base_folder']
        ignore_files = [v for v in preset.get('ignore_files', None)] if preset.get('ignore_files', None) else None
        
        make_hl_pak(game_path, out_path, also_include_overwrites=also_include, ignore_files=ignore_files, use_tqdm=True)

        # Check if the output folder exists
        if not out_path.exists():
            print(f'Error: Output folder {out_path} does not exist.')
            exit(1)
        
        # Push the output folder to the device(s)
        # Make sure xash folder exists
        make_xash_folder(quest_devices)
        remote_folder = Path('/sdcard/xash') / preset['base_folder']
        print(f'Pushing {out_path} to device(s) at {remote_folder}')
        for device in quest_devices:
            push_folder(device, out_path, remote_folder)
            # copy_all_files(device, out_path, remote_folder)


def look_for_hl_gold_zip_in_downloads():
    # Look for the HL Gold HD zip in the downloads folder
    downloads_folder = Path.home() / 'Downloads'
    if (downloads_folder / 'hl_gold_hd.zip').exists():
        return downloads_folder / 'hl_gold_hd.zip'


if __name__ == '__main__':
    # Look for quest devices
    quest_devices = find_quest_devices()
    print(quest_devices)
    if not quest_devices:
        print('No Quest devices found.')
        exit(1)
    
    # Install the APKs for the launcher and the game
    install_lambda_and_launcher(quest_devices)

    base_path = Path(search_for_halflife())
    pack_and_copy_preset(quest_devices, base_path=base_path, preset='hl_hd')

    zip_file = look_for_hl_gold_zip_in_downloads()
    download_and_install_hl_gold(base_path, zip_file)
    pack_and_copy_hl_gold(quest_devices, base_path=base_path)

    if base_path / 'bshift':
        # Copy Blueshift
        pack_and_copy_preset(quest_devices, base_path=base_path, preset='blueshift_hd')
    
    if base_path / 'gearbox':
        # Copy opposing force
        pack_and_copy_preset(quest_devices, base_path=base_path, preset='opfor_hd')
