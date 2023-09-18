# Thanks to Tome Of Preach for the basis of this script
# Originally found here: https://tomeofpreach.wordpress.com/2013/06/22/makepak-py/
import os
import math
import shutil
import struct
from tqdm import tqdm
from pathlib import Path


MAX_FILES_PER_PAK = 3900
 
#dummy class for stuffing the file headers into
class FileEntry:
    pass
 

def dir_to_pak(rootdir, pakfilename):
    # Rootdir is the directory to be packed
    # Pakfilename is the name of the pak file to be created
    
    pakfile = open(pakfilename,"wb")
    
    # write a dummy header to start with
    pakfile.write(struct.Struct("<4s2l").pack(b"PACK",0,0))
    
    # walk the directory recursively, add the files and record the file entries
    offset = 12
    fileentries = []
    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            entry = FileEntry()
            impfilename = os.path.join(root,file)  
            entry.filename = os.path.relpath(impfilename,rootdir).replace("\\","/")       
            with open(impfilename, "rb") as importfile:
                pakfile.write(importfile.read())
                entry.offset = offset
                entry.length = importfile.tell()
                offset = offset + entry.length
            fileentries.append(entry)
    tablesize = 0
    
    # after all the file data, write the list of entries
    for entry in fileentries:
        pakfile.write(struct.Struct("<56s").pack(entry.filename.encode("ascii")))
        pakfile.write(struct.Struct("<l").pack(entry.offset))
        pakfile.write(struct.Struct("<l").pack(entry.length))
        tablesize = tablesize + 64
    
    # return to the header and write the values correctly
    pakfile.seek(0)
    pakfile.write(struct.Struct("<4s2l").pack(b"PACK",offset,tablesize))
    pakfile.close()


def make_hl_pak(in_path: Path, out_path: Path, also_include_overwrites: list=None, ignore_files: list=None, print_fcn: callable=print, verbose: bool=False, max_chunk_size: int=MAX_FILES_PER_PAK, use_tqdm: bool=True):
    # First, make the output directory if it doesn't exist
    out_path = Path(out_path)
    # Delete the output directory if it already exists
    if out_path.exists():
        shutil.rmtree(out_path)
    # Ensure the output path exists
    out_path.mkdir(parents=True)

    # Get a list of all of the base HL files
    base_files = list(Path(in_path).rglob("*"))
    # Copy all of the base HL files to the output directory, preserving directory structure
    print_fcn(f'Copying files from {in_path} to output directory...')

    if use_tqdm:
        file_iter = tqdm(base_files)
    else:
        file_iter = base_files

    for file in file_iter:
        if file.is_file():
            # Check if this file should be ignored
            if ignore_files and file.name in ignore_files:
                print_fcn(f'  Skipping {file}')
                continue

            # Create necessary subdirectories in dst
            relative_path = file.relative_to(in_path)
            new_dst = out_path / relative_path.parent
            new_dst.mkdir(parents=True, exist_ok=True)
            # Copy file to new destination
            if verbose:
                print_fcn(f'Copying {file} to {new_dst}')
            shutil.copy(file, new_dst)
    print_fcn(f'Copy complete.\n')

    # Copy all of the files from the overwrites to the output directory, preserving directory structure
    if also_include_overwrites:
        for path in also_include_overwrites:
            new_dir = Path(path)
            if not new_dir.exists():
                print_fcn(f'Error: {new_dir} does not exist, skipping.')
                continue
            print_fcn(f'Copying files from {new_dir} to output directory...')
            files = list(Path(new_dir).rglob("*"))

            if use_tqdm:
                file_iter = tqdm(files)
            else:
                file_iter = files
            for file in file_iter:
                if file.is_file():
                    # Check if this file should be ignored
                    if ignore_files and file.name in ignore_files:
                        print_fcn(f'  Skipping {file}')
                        continue

                    # Create necessary subdirectories in dst
                    relative_path = file.relative_to(new_dir)
                    new_dst = out_path / relative_path.parent
                    new_dst.mkdir(parents=True, exist_ok=True)
                    # Copy file to new destination
                    if verbose:
                        print_fcn(f'Copying {file} to {new_dst}')
                    shutil.copy(file, new_dst)
            print_fcn(f'Copy complete.\n')

    # Bundle up all of the subdirectories into pak files
    # Split files into chunks, put each chunk into a pak file
    pak_num = 0
    print_fcn(f'Output path: {out_path}')
    final_files = list(Path(out_path).rglob("*"))
    num_files = len(final_files)

    # Switch to the output directory
    os.chdir(out_path)
    pak_files_source_dir = Path(out_path / 'pak_files')
    pak_files_source_dir.mkdir(parents=True, exist_ok=True)

    # Iterate through the files and move them into pak files if appropriate
    file_iter = tqdm(final_files, desc='Staging files for pak_files') if use_tqdm else final_files
    for file in file_iter:
        if file.is_dir():
            # This is a directory, don't try to copy it
            continue
        # Filter out viewmodels, they start with v_ and end with .mdl
        if file.name.startswith('v_') and file.name.endswith('.mdl'):
            print_fcn(f'  Skipping viewmodel: {file}')
            # Delete it from the output directory
            file.unlink()
            continue

        relpath: Path = file.relative_to(out_path)
        # If it's in the root, don't do anything
        if relpath.parent == Path():
            continue

        # Put the file in the pak_files dir, keeping the directory structure
        if len(str(relpath)) > 56:
            # This file is too long!
            print_fcn(f'  Error: path {relpath} is too long for pak file (56 char limit). Skipping.')
        else:
            # Move the file to the pak_files dir
            if verbose:
                print_fcn(f'  adding: {relpath}')
            # Create necessary subdirectories in dst
            new_dst = pak_files_source_dir / relpath.parent
            new_dst.mkdir(parents=True, exist_ok=True)
            # Move file to new destination
            shutil.move(file, pak_files_source_dir / relpath)

    # Break the pak_files dir into chunks if there are more than max_chunk_size files in it
    pak_files = list(Path(pak_files_source_dir).rglob("*"))
    num_pak_files = len(pak_files)
    if num_pak_files > max_chunk_size:
        # Split the directory into however many chunks are needed
        num_chunks = math.ceil(num_pak_files / max_chunk_size)
        for i in range(0, num_chunks):
            # Create a new pak_files dir for each chunk
            new_pak_files_dir = pak_files_source_dir / f'pak_files_{i}'
            new_pak_files_dir.mkdir(parents=True, exist_ok=True)
            for file in pak_files[i * max_chunk_size: (i + 1) * max_chunk_size]:
                if file.is_dir():
                    # This is a directory, don't try to copy it
                    continue
                relpath: Path = file.relative_to(out_path)
                relpath: Path = file.relative_to(out_path)
                # Create necessary subdirectories in dst
                new_dst = new_pak_files_dir / relpath.parent
                new_dst.mkdir(parents=True, exist_ok=True)
                # Move file to new destination
                shutil.move(file, new_pak_files_dir / relpath)

            # Create a pak file for this chunk
            pak_name = f'pak{pak_num}.pak'  # e.g. pak0.pak, pak1.pak, etc.
            pak_path = out_path / pak_name
            print_fcn(f'Creating pak file: {pak_name}')
            dir_to_pak(str(new_pak_files_dir / 'pak_files'), pak_path)
            # Delete the pak_files dir
            shutil.rmtree(new_pak_files_dir)
            pak_num += 1
    else:
        # Create a pak file for the pak_files dir
        pak_name = f'pak{pak_num}.pak'
        pak_path = out_path / pak_name
        print_fcn(f'Creating pak file: {pak_name}')
        dir_to_pak(str(pak_files_source_dir), pak_path)

    # Delete the pak_files dir
    shutil.rmtree(pak_files_source_dir)

    # Loop through the empty dirs and add a KEEP_ME file to each one to preserve the directory structure
    empty_dirs = list(Path(out_path).rglob("*"))
    for dir in empty_dirs:
        if dir.is_dir() and not list(dir.rglob("*")):
            # This directory is empty
            keep_me_file = dir / 'KEEP_ME'
            keep_me_file.touch()

