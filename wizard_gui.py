import PySimpleGUI as sg
from pathlib import Path

from presets import search_for_halflife, presets
from adb_util import find_quest_devices, rewrite_path_for_os
from wizard import install_lambda_and_launcher, pack_and_copy_hl_gold, pack_and_copy_preset, download_and_install_hl_gold, look_for_hl_gold_zip_in_downloads


def do_a_preset(preset_name: str):
    # Look for quest devices
    quest_devices = find_quest_devices()

    if not quest_devices:
        sg.popup('Please find Quest devices first.')
    else:
        base_path = Path(search_for_halflife())
        preset = presets[preset_name]
        game_path = base_path / preset['base_folder']
        if not rewrite_path_for_os(game_path).exists():
            sg.popup(f'Error: Game path {game_path} does not exist.')
            return
        
        if preset['also_include_overwrites']:
            for new_folder in preset['also_include_overwrites']:
                if not rewrite_path_for_os(base_path / new_folder).exists():
                    sg.popup(f'Error: {base_path / new_folder} does not exist.')
                    return
        
        # Pack and copy the preset
        pack_and_copy_preset(quest_devices, base_path=base_path, preset=preset_name)
        sg.popup(f'{preset_name} copied successfully.')


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
        [sg.Button('Pack and Copy HL AI Upscale')],
        [sg.Button('Pack and Copy Blueshift AI Upscale')],
        [sg.Button('Pack and Copy Opposing Force AI Upscale')],
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

                install_lambda_and_launcher(quest_devices, force_install=True)
                sg.popup('Lambda and Launcher installed successfully.')

        if event == 'Pack and Copy Base Half-Life':
            do_a_preset('hl_hd')

        if event == 'Download and Install HL Gold HD':
            if not quest_devices:
                sg.popup('Please find Quest devices first.')
            else:
                base_path = Path(search_for_halflife())
                zip_file = look_for_hl_gold_zip_in_downloads()
                
                download_and_install_hl_gold(base_path, zip_file, force_install=True)
                sg.popup('HL Gold downloaded and installed successfully.')

        if event == 'Pack and Copy HL Gold HD':
            if not quest_devices:
                sg.popup('Please find Quest devices first.')
            else:
                base_path = Path(search_for_halflife())
                if not base_path / 'HL_Gold_HD':
                    sg.popup('HL Gold HD not found.')
                else:
                    pack_and_copy_hl_gold(quest_devices, base_path=base_path)
                    sg.popup('HL Gold packed and copied successfully.')

        if event == 'Pack and Copy Blueshift':
            do_a_preset('blueshift_hd')

        if event == 'Pack and Copy Opposing Force':
            do_a_preset('opfor_hd')
        
        if event == 'Pack and Copy HL AI Upscale':
            do_a_preset('hl_ai_upscale')
        
        if event == 'Pack and Copy Blueshift AI Upscale':
            do_a_preset('blueshift_ai_upscale')

        if event == 'Pack and Copy Opposing Force AI Upscale':
            do_a_preset('opfor_ai_upscale')


    # Close the GUI window
    window.close()


if __name__ == '__main__':
    main()
