import PySimpleGUI as sg
from pathlib import Path

from presets import search_for_halflife
from adb_util import find_quest_devices
from wizard import install_lambda_and_launcher, pack_and_copy_hl_gold, pack_and_copy_preset, download_and_install_hl_gold, look_for_hl_gold_zip_in_downloads


def main():
    # Define the GUI layout
    layout = [
        [sg.Button('Find Quest Devices')],
        [sg.Button('Install Lambda and Launcher')],
        [sg.Button('Pack and Copy Base Half-Life')],
        [sg.Button('Download and Install HL Gold HD')],
        [sg.Button('Pack and Copy HL Gold HD')],
        [sg.Button('Pack and Copy Blueshift')],
        [sg.Button('Pack and Copy Opposing Force')],
        [sg.Button('Exit')]
    ]

    # Create the GUI window
    window = sg.Window('HL Packer Wizard', layout)

    # Look for quest devices
    quest_devices = find_quest_devices()

    # Run the GUI loop
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        if event == 'Find Quest Devices':
            quest_devices = find_quest_devices()
            if not quest_devices:
                sg.popup('No Quest devices found.')
            else:
                sg.popup(f'Found Quest devices: {quest_devices}')

        if event == 'Install Lambda and Launcher':
            if not quest_devices:
                sg.popup('Please find Quest devices first.')
            else:
                if not sg.popup_yes_no('Are you sure you want to install Lambda and Launcher? This will overwrite any existing installations.'):
                    continue

                # Show a please wait screen
                sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)

                install_lambda_and_launcher(quest_devices, force_install=True)

                # Delete the please wait screen
                sg.popup_animated(None)
                sg.popup('Lambda and Launcher installed successfully.')

        if event == 'Pack and Copy Base Half-Life':
            if not quest_devices:
                sg.popup('Please find Quest devices first.')
            else:
                base_path = Path(search_for_halflife())
                if not base_path.exists():
                    sg.popup(f'Error: Half-Life cannot be found, please ensure it is installed.')
                    continue
                # Show a please wait screen
                sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
                # Pack and copy the base Half-Life
                pack_and_copy_preset(quest_devices, base_path=base_path, preset='hl_hd')
                # Delete the please wait screen
                sg.popup_animated(None)

                sg.popup('Base Half-Life packed and copied successfully.')

        if event == 'Download and Install HL Gold HD':
            if not quest_devices:
                sg.popup('Please find Quest devices first.')
            else:
                base_path = Path(search_for_halflife())
                zip_file = look_for_hl_gold_zip_in_downloads()
                # Show a please wait screen
                sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
                download_and_install_hl_gold(base_path, zip_file, force_install=True)

                # Delete the please wait screen
                sg.popup_animated(None)
                sg.popup('HL Gold downloaded and installed successfully.')

        if event == 'Pack and Copy HL Gold HD':
            if not quest_devices:
                sg.popup('Please find Quest devices first.')
            else:
                base_path = Path(search_for_halflife())
                if not base_path / 'HL_Gold_HD':
                    sg.popup('HL Gold HD not found.')
                else:
                    # Show a please wait screen
                    sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)    
                    pack_and_copy_hl_gold(quest_devices, base_path=base_path)
                    # Delete the please wait screen
                    sg.popup_animated(None)
                    sg.popup('HL Gold packed and copied successfully.')

        if event == 'Pack and Copy Blueshift':
            if not quest_devices:
                sg.popup('Please find Quest devices first.')
            else:
                base_path = Path(search_for_halflife())
                if base_path / 'bshift':
                    # Show a please wait screen
                    sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
                    pack_and_copy_preset(quest_devices, base_path=base_path, preset='blueshift_hd')
                    # Delete the please wait screen
                    sg.popup_animated(None)
                    sg.popup('Blueshift copied successfully.')
                else:
                    sg.popup('Blueshift not found.')

        if event == 'Pack and Copy Opposing Force':
            if not quest_devices:
                sg.popup('Please find Quest devices first.')
            else:
                base_path = Path(search_for_halflife())
                if base_path / 'gearbox':
                    # Show a please wait screen
                    sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
                    pack_and_copy_preset(quest_devices, base_path=base_path, preset='opfor_hd')
                    # Delete the please wait screen
                    sg.popup('Opposing Force copied successfully.')
                else:
                    sg.popup('Opposing Force not found.')

    # Close the GUI window
    window.close()


if __name__ == '__main__':
    main()
