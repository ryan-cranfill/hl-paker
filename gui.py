import PySimpleGUI as sg
from pathlib import Path
from pak_util import make_hl_pak
from presets import presets, search_for_halflife

sg.theme('DarkAmber')

def show_presets():
    preset_list = ['\nAvailable presets:']
    preset_list.append('=' * 20)
    for key, value in presets.items():
        preset_list.append(f'{key}: {value["description"]}\n')
    return '\n'.join(preset_list)

def tuple_string_to_list(string):
    if string.startswith('(') and string.endswith(')'):
        # Turn a string like ('val1', 'val2') into ['val1', 'val2']
        strings = [v.strip() for v in string[1:-1].split(',')]
        # Remove quotes and empty strings
        return [v.strip("'") for v in strings if v]
    else:
        # It's a string that looks like val1, val2 so just split on the comma
        return [v.strip() for v in string.split(',')]

base_path = search_for_halflife()
default_preset = 'hl_hd'
preset = presets[default_preset]

layout = [
    [sg.Text('Preset', tooltip='Select a preset from the dropdown'), sg.Combo(list(presets.keys()), key='preset', enable_events=True, default_value=default_preset)],
    [sg.Multiline(preset['description'], size=(50, 10), key='preset_description')],
    [sg.Text('Half-Life Base Path', tooltip='Enter the base path for Half-Life'), sg.Input(key='hl_base_path', default_text=search_for_halflife(), expand_x=True,), sg.FolderBrowse()],
    [sg.Text('Game Path', tooltip='Enter the path to the game, relative to the base path.'), sg.Input(key='game_path', default_text=preset['base_folder'], expand_x=True,)],
    [sg.Text('Max Chunk Size', tooltip='Maximum amount of files per .pak (do not exceed 4000).'), sg.Input(key='max_chunk_size', default_text=3999)],
    [sg.Text('Also Include', tooltip='Enter any additional directories relative to the base path to copy over, comma separated'), sg.Input(key='also_include', default_text=preset['also_include_overwrites'], expand_x=True,)],
    [sg.Text('Ignore Files', tooltip='Enter any files to ignore, comma separated'), sg.Input(key='ignore_files', default_text=preset.get('ignore_files', None), expand_x=True,)],
    [sg.Checkbox('Verbose', key='verbose')],
    [sg.Text('Output Path', tooltip='Enter the output path for the PAK files'), sg.Input(key='out_path', default_text='xash')],
    [sg.Button('Show Presets'), sg.Button('Start')],
    [sg.Output(size=(400, 20), key='output', echo_stdout_stderr=True, font='Courier 10', text_color='white', background_color='black', pad=(0, 0), tooltip='Output from the program will be displayed here.', expand_y=True, expand_x=True)],
]

window = sg.Window('Half-Life PAK Creator', layout, size=(800, 800))

while True:
    event, values = window.read()
    output = window['output']

    if event == sg.WINDOW_CLOSED:
        break
    
    elif event == 'Show Presets':
        sg.popup(show_presets())
    
    elif event == 'preset':
        preset = presets[values['preset']]
        window['game_path'].update(preset['base_folder'])
        also_include_string = ', '.join(preset['also_include_overwrites']) if preset['also_include_overwrites'] else ''
        ignore_files_string = ', '.join(preset.get('ignore_files', None)) if preset.get('ignore_files', None) else ''
        window['also_include'].update(also_include_string)
        window['preset_description'].update(preset['description'])
        window['ignore_files'].update(ignore_files_string)

    elif event == 'Start':
        # Here you would call the function to create the pak files, passing in the values from the form
        print('Starting...')
        base_path = Path(values['hl_base_path'])
        game_path = base_path / values['game_path']
        also_include = [base_path / new_folder for new_folder in tuple_string_to_list(values['also_include'])] if values['also_include'] else None
        out_path = base_path / values['out_path'] / values['game_path']
        ignore_files = [v for v in tuple_string_to_list(values['ignore_files'])] if values['ignore_files'] else None
        verbose = values['verbose']
        max_chunk_size = int(values['max_chunk_size'])

        # print(values['also_include'], type(values['also_include']), tuple_string_to_list(values['also_include']))
        # print(ignore_files)
        # print(also_include)
        make_hl_pak(game_path, out_path, also_include_overwrites=also_include, max_chunk_size=max_chunk_size, verbose=verbose, ignore_files=ignore_files, use_tqdm=False)
        
        print(f'Done. Place the contents of the output folder ({out_path}) in /sdcard/xash/')

window.close()