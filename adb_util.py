import os
import zipfile
import requests
import subprocess
from tqdm import tqdm
from pathlib import Path
from tempfile import TemporaryDirectory
from ppadb.client import Client as AdbClient
from ppadb.device import Device

from presets import APK_CONFIGS, HL_GOLD_HD_URL, ADB_ZIP, TQDM_AVAILABLE


IS_WINDOWS = os.name == 'nt'

def rewrite_path_for_os(path: Path) -> Path:
    if IS_WINDOWS:
        return Path(str(path).replace('/', '\\'))

    return Path(str(path).replace('\\', '/'))

def find_quest_devices():
    client = AdbClient()
    devices: list[Device] = client.devices()

    quest_devices = []
    for device in devices:
        props = device.get_properties()
        # Get the device model, check if it's a quest
        if 'quest' in props.get('ro.product.model', '').lower():
            quest_devices.append(device)
    
    return quest_devices


def get_adb_exe() -> (Path, Path):
    # Unzip the adb zip to a temporary directory and return the path to the adb executable and the temporary directory
    temp_dir = TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    print('Extracting ADB zip to', temp_dir_path)
    with zipfile.ZipFile(ADB_ZIP, 'r') as zip_ref:
        zip_ref.extractall(temp_dir_path)

    # Get the path to the adb executable
    adb_exe = temp_dir_path / 'platform-tools' / 'adb.exe'
    print('ADB executable:', adb_exe)
    return adb_exe, temp_dir

def delete_temp_dir(temp_dir: TemporaryDirectory):
    # Delete the temporary directory
    print('Deleting temporary directory', temp_dir.name)
    temp_dir.cleanup()
    print('Deleted temporary directory.')

def download_with_progress(url, dest_path):
    # with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=dest_path) as t:
    #     urllib.request.urlretrieve(url, dest_path, reporthook=reporthook(t))
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            if TQDM_AVAILABLE:
                pbar = tqdm(total=int(r.headers['Content-Length']))
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                    pbar.update(len(chunk))
                pbar.close()
            else:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

def install_apk(apk_url, device: Device):
    with TemporaryDirectory() as temp_dir:
        # Get the filename from the URL
        apk_filename = apk_url.split('/')[-1]
        # Download the APK
        apk_path = Path(temp_dir) / apk_filename

        print('Downloading APK...')
        download_with_progress(apk_url, apk_path)
        print('\nDownloaded APK.')
        # Install the APK
        print('Installing APK...')
        adb_exe, temp_dir = get_adb_exe()
        subprocess.run([str(adb_exe), '-s', device.serial, 'install', '-r', str(apk_path)])
        # device.install(apk_path, reinstall=True)
        delete_temp_dir(temp_dir)
        print('Installed APK.')

def make_folder(device: Device, folder: Path):
    # Check that it starts with /sdcard/
    if not folder.parts[0] == 'sdcard':
        # Make it start with /sdcard/
        folder = Path('/sdcard') / folder

    # Make the folder on the device's sdcard
    device.shell(f'mkdir {folder}')
    print(f'Made {folder} on device.')

def push_folder(device: Device, local_folder: str, remote_folder: Path):
    # Check that it starts with /sdcard/
    if not remote_folder.parts[0] == 'sdcard':
        # Make it start with /sdcard/
        remote_folder = Path('/sdcard') / remote_folder
    
    if IS_WINDOWS:
        # Have to use subprocess because the ppadb push function doesn't work on Windows
        # Replace \ with / in the remote folder
        remote_folder = str(remote_folder).replace('\\', '/')
        print('remote_folder:', remote_folder)
        print('Current directory:', os.getcwd())
        adb_exe, temp_dir = get_adb_exe()
        subprocess.run([str(adb_exe), '-s', device.serial, 'push', str(local_folder), str(remote_folder)])
        delete_temp_dir(temp_dir)
    else:
         # # Make sure the local folder ends with a / so that it copies the contents of the folder instead of the folder itself
        if not str(local_folder).endswith('/'):
            local_folder = str(local_folder) + '/'
        # Push the folder to the device's sdcard
        device.push(local_folder, str(remote_folder))

    print(f'Pushed {local_folder} to {remote_folder} on device.')

def copy_all_files(device: Device, src: Path, dest: Path):
    # Traverse the src directory and copy all files to the dest directory
    # Check that it starts with /sdcard/
    if not dest.parts[0] == 'sdcard':
        # Make it start with /sdcard/
        dest = Path('/sdcard') / dest
    
    # Loop through the files in src
    for file in src.rglob('*'):
        print('pushing:', file)
        # Get the relative path of the file
        relative_path = file.relative_to(src)
        
        # If it's a directory, create it on the device
        if file.is_dir():
            # Get the relative path of the file
            relative_path = file.relative_to(src)
            # Make the folder on the device's sdcard
            device.shell(f'mkdir {dest / relative_path}')
            # device.shell(f'mkdir {dest / file.name}')
            # device.shell(f'mkdir {dest / file.name}')
            print(f'Made {dest / relative_path} on device.')
        # If it's a file, push it
        elif file.is_file():
            
            # Push the file to the device
            device.push(str(file), str(dest / relative_path))
            print(f'Pushed {file} to {dest / relative_path} on device.')

def check_if_app_installed(device: Device, package_name: str):
    # Check if the app is installed
    packages = device.shell('pm list packages')
    # print('Installed packages:', packages)
    if package_name in packages:
        return True
    else:
        return False

def install_hl_gold_hd(base_path: Path, zip_path: Path = None):
    # Download the HL Gold HD zip to a temporary directory
    with TemporaryDirectory() as temp_dir:
        if zip_path is not None:
            if zip_path.exists():
                print(f'Using existing zip at {zip_path}.')
            else:
                print(f'Error: Zip path {zip_path} does not exist.')
                exit(1)
        else:
            zip_path = Path(temp_dir) / 'hl_gold_hd.zip'
            download_with_progress(HL_GOLD_HD_URL, zip_path)
        
        # Extract the zip 
        print('Extracting zip...')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # There is the HL_Gold_HD folder inside the zip, so extract that to the base path
            # Ignore the How_to_install.txt and commandline.txt files
            iterator = tqdm(zip_ref.infolist()) if TQDM_AVAILABLE else zip_ref.infolist()
            for zip_info in iterator:
                if zip_info.filename.endswith('.txt'):
                    continue
                # We need to rewrite the path to remove the "hl gold" folder and make it just start with "HL_Gold_HD"
                zip_info.filename = zip_info.filename.replace('hl gold/', '')
                # Extract the file
                if zip_info.filename:
                    zip_ref.extract(zip_info, base_path)
        print('Extracted zip.')

def main():
    # Get the device
    quest_devices = find_quest_devices()
    print(quest_devices)
    # Install the APKs
    for apk_url in APK_CONFIGS['quest'].values():
        for device in quest_devices:
            print(f'Installing {apk_url} to {device.get_properties()["ro.product.model"]}...')
            install_apk(apk_url, device)


if __name__ == '__main__':
    main()