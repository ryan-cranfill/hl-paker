import zipfile
import requests
import urllib.request
from tqdm import tqdm
from pathlib import Path
from tempfile import TemporaryDirectory
from ppadb.client import Client as AdbClient
from ppadb.device import Device

from presets import APK_CONFIGS, HL_GOLD_HD_URL


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


def reporthook(t):
    """
    :param t: tqdm instance
    :return: updated tqdm instance
    """
    last_b = [0]

    def inner(b=1, bsize=1, tsize=None):
        """
        :param b: int option
        :param bsize: int option
        :param tsize: int option
        :return: updated tqdm instance
        """
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b
        return t

    return inner

def download_with_progress(url, dest_path):
    # with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=dest_path) as t:
    #     urllib.request.urlretrieve(url, dest_path, reporthook=reporthook(t))
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            pbar = tqdm(total=int(r.headers['Content-Length']))
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    pbar.update(len(chunk))

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
        device.install(apk_path, reinstall=True)
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
    
    # Make sure the local folder ends with a / so that it copies the contents of the folder instead of the folder itself
    if not str(local_folder).endswith('/'):
        local_folder = str(local_folder) + '/'

    # Push the folder to the device's sdcard
    device.push(local_folder, str(remote_folder))
    print(f'Pushed {local_folder} to {remote_folder} on device.')

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
            for zip_info in tqdm(zip_ref.infolist()):
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