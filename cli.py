from pathlib import Path
from pak_util import make_hl_pak
from argparse import ArgumentParser

from presets import presets, search_for_halflife


def show_presets():
    print('\nAvailable presets:')
    print('=' * 20)
    for key, value in presets.items():
        print(f'{key}: {value["description"]}\n')


def main():
    # Create ArgumentParser object
    parser = ArgumentParser(description='Create pak files from Half-Life directory.')
    parser.add_argument('--preset', help='Preset to use. If not using a preset, must specify game_path and also_include if desired.')
    parser.add_argument('--game_path', help='Path to game directory to create pak files for if not using a preset. For example, for Half-Life this would be the full path to Half-Life\\valve.')
    parser.add_argument('--hl_base_path', default=search_for_halflife(), help='Path to base Half-Life directory (one dir up from \\valve\). Will search for Half-Life directory if not specified.')
    parser.add_argument('--max_chunk_size', default=3900, help='Max number of files per pak file.', type=int)
    parser.add_argument('--also_include', action='append', help='Folders to also include in pak files.')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output.')
    parser.add_argument('--out_path', default='xash', help='Output directory for pak files relative to hl_base_path. Defaults to \\xash in the Half-Life directory.')
    parser.add_argument('--show-presets', action='store_true', help='Show available presets and exit.')
    args = parser.parse_args()

    # If show-presets was specified, show the presets and exit
    if args.show_presets:
        show_presets()
        return
    
    max_chunk_size = args.max_chunk_size
    verbose = args.verbose

    # If a preset was specified, use that
    if args.preset:
        if args.preset not in presets:
            print(f'Error: Preset {args.preset} not found.')
            show_presets()
            return
        
        base_path = Path(args.hl_base_path)
        print(f'Base path: {base_path}')
        
        preset = presets[args.preset]
        game_path = base_path / preset['base_folder']
        also_include = [base_path / new_folder for new_folder in preset['also_include_overwrites']] if preset['also_include_overwrites'] else None
        out_path = base_path / args.out_path / preset['base_folder']
        ignore_files = preset.get('ignore_files', None)
        print(f'Game path: {game_path}')
        print(f'Also include: {also_include}')
        print(f'Out path: {out_path}')
        make_hl_pak(game_path, out_path, also_include_overwrites=also_include, max_chunk_size=max_chunk_size, verbose=verbose, ignore_files=ignore_files)
        commandline = preset.get('commandline', None)
        if commandline:
            # Write out commandline.txt to the output directory
            commandline_path = out_path.parent / 'commandline.txt'
            print(f'Writing commandline to {commandline_path}...')
            with open(commandline_path, 'w') as f:
                f.write(commandline)
        return
    
    # If a preset was not specified, use the game_path and also_include arguments
    if not args.game_path:
        print('Error: Must specify either a preset or a game_path. Use --show-presets to see available presets.')
        return
    
    game_path = Path(args.game_path)
    if not game_path.exists():
        print(f'Error: {game_path} does not exist.')
        return
    
    also_include = args.also_include
    also_include = [base_path / new_folder for new_folder in preset['also_include_overwrites']] if preset['also_include_overwrites'] else None
    out_path = args.hl_base_path / args.out_path / game_path.name
    make_hl_pak(game_path, out_path, also_include_overwrites=also_include, max_chunk_size=max_chunk_size, verbose=verbose)
    return

if __name__ == '__main__':
    main()
