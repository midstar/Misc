# This is a tool useful for handling Emulator ROM files

import argparse, os, shutil, filecmp, zipfile, tempfile

TEMPDIR = os.path.join(tempfile.gettempdir(), 'romtool')

def remove_numbering(filename):
    if ' ' in filename and filename[:filename.index(' ')].isnumeric():
        filename = filename[filename.index(' ') + 1:] 
    return filename

def extension(filename):
    return os.path.splitext(filename)[-1][1:].lower()

def listfiles(path, ext):
    filenames = []
    for filename in os.listdir(path):  
        pathname = os.path.join(path,filename)
        if not os.path.isfile(pathname): continue
        if ext.lower() not in ['*', extension(filename)]: continue
        filenames.append(filename)
    filenames.sort()
    return filenames

def remove_brackets(filename,start,stop):
    while start in filename and stop in filename:
        start_i = filename.index(start)
        stop_i  = filename.index(stop)
        if stop_i < start_i:
            break
        filename = filename[:start_i] + filename[stop_i + 1:]
    return filename


def approximate_match(src_file, dst_file):
    src_file = os.path.splitext(src_file)[0]
    dst_file = os.path.splitext(dst_file)[0]

    src_file = remove_numbering(src_file).lower()
    dst_file = remove_numbering(dst_file).lower()

    for start, stop in [('(',')'),('[',']'),('<','>')]:
        src_file = remove_brackets(src_file, start, stop)
        dst_file = remove_brackets(dst_file, start, stop)

    for c in '!@#$%^&*()[]{};:,./<>?\|"\'`~-=_+ ':
        src_file = src_file.replace(c,'')
        dst_file = dst_file.replace(c,'')

    if src_file == dst_file:
        return True
    return False

# Returns (match, name1, name2, same_name, same_content, size1, size2)
def diff_file(src_file, dst_file, src, dst):
    if src_file == dst_file:
        same_name = True
    elif approximate_match(src_file, dst_file):
        same_name = False
    else:
        return (False, src_file, dst_file, False, False, 0, 0)

    src_path = os.path.join(src,src_file)
    dst_path = os.path.join(dst,dst_file)
    src_size = os.stat(src_path).st_size
    dst_size = os.stat(dst_path).st_size

    if src_size == dst_size:
        if filecmp.cmp(src_path,dst_path, shallow=False):
            return (True, src_file, dst_file, same_name, True, src_size, dst_size)
    
    if extension(src_file) == 'zip' or extension(dst_file) == 'zip':
        if extension(src_file) == 'zip':
            src_path, src_size = extract_zip(src_path, 'src')
        if extension(dst_file) == 'zip':
            dst_path, dst_size = extract_zip(dst_path, 'dst')
        if src_path != '' and dst_path != '':
            same = src_size == dst_size and filecmp.cmp(src_path,dst_path, shallow=False)
            shutil.rmtree(TEMPDIR) # Clean-up
            if same:
                return (True, src_file, dst_file, same_name, True, src_size, dst_size)

    return (True, src_file, dst_file, same_name, False, src_size, dst_size)

def print_diff(match, filename1, filename2, same_name, same_content, size1, size2):
    if match:
        print(filename1,'=', filename2)
        if same_name:
            print('   - Exact filename match')
        else:
            print('   - Approximate filename match')
        if same_content:
            print('   - File contents is identical')
        elif size1 == size2:
            print(f'   - Files contents are not identical but has same size ({size1} bytes)')
        else:
            print(f'   - File size differs ({size1} vs {size2} bytes)')



def diff(src, dst, ext):
    src_files = listfiles(src, ext)
    dst_files = listfiles(dst, ext)

    for src_file in src_files:
        unique = True
        for dst_file in dst_files:
            diff_res = diff_file(src_file, dst_file, src, dst)
            if diff_res[0]:
                print_diff(*diff_res)
                unique = False
        if unique: print(src_file, '(unique)')

def dup(dir, ext, delete_identical):
    files = listfiles(dir, ext)

    while files:
        file = files.pop()
        for file2 in files:
            diff_res = diff_file(file, file2, dir, dir)
            if diff_res[0]:
                print_diff(*diff_res)
                if delete_identical:
                    print()
                    print(f'[1]   {file}')
                    print(f'[2]   {file2}')
                    print()
                    answer = input(f'Select file to remove or enter for none [1/2]:')
                    file_delete = ''
                    if answer == '1':
                        file_delete = file
                    elif answer == '2':
                        file_delete = file2
                        files.remove(file2)
                    else:
                        continue
                    print('   - Deleting file', file_delete)
                    os.remove(os.path.join(dir,file_delete))
                    break


def replace(dir, org, new, ext):
    files = listfiles(dir, ext)

    for filename in files:
        if org in filename:
            filename_new = filename.replace(org,new)
            pathname = os.path.join(dir,filename)
            pathname_new = os.path.join(dir,filename_new)
            print(filename,'->', filename_new)
            os.rename(pathname, pathname_new)

# Extract file from zip return (extracted_file_path, size)
# Only works for zip files containing 1 file
def extract_zip(path, unzip_path = ''):

    out_path = os.path.join(TEMPDIR, unzip_path)
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    with zipfile.ZipFile(path,'r') as zip:
        namelist = zip.namelist()
        if len(namelist) != 1: return ('', 0)
        zip_internal_path = namelist[0]
        zip.extract(zip_internal_path, path=out_path)
        new_path = os.path.join(out_path, zip_internal_path)
        return (new_path, os.stat(new_path).st_size)

def zip(dir, ext, delete):
    files = listfiles(dir, ext)

    for filename in files:
        if extension(filename) != 'zip':
            zip_filename = os.path.splitext(filename)[0]+'.zip'
            pathname = os.path.join(dir,filename)
            pathname_zip = os.path.join(dir,zip_filename)
            if not os.path.exists(pathname_zip):
                print(filename, ' -> ', zip_filename)
                with zipfile.ZipFile(pathname_zip,'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zip: 
                    zip.write(pathname) 
                if delete:
                    os.remove(pathname)

def unzip(dir, delete):
    files = listfiles(dir, 'zip')

    for filename in files:
        pathname = os.path.join(dir,filename)
        with zipfile.ZipFile(pathname,'r') as zip:
            print(filename, ' -> ', *zip.namelist())
            zip.extractall(dir)
        if delete:
            os.remove(pathname)

def copy(src, dst, ext, remove_numbers, remove_similar):
    src_files = listfiles(src, ext)
    dst_files = listfiles(dst, ext)

    for src_file in src_files:
        dst_tmp = dst_files[:]
        for dst_file in dst_tmp:
            match, _, _, same_name, same_content, _, _ = diff_file(src_file, dst_file, src, dst)
            if match and remove_similar:
                if not same_content:
                    print()
                    print(f'"{src_file}" at source has similar file at dest:')
                    answer = input(f'   - "{dst_file}" remove? [y/N]:')
                    if answer.lower() == 'n':
                        continue
                dst_files.remove(dst_file)
                os.remove(os.path.join(dst,dst_file))

        path_src = os.path.join(src,src_file)
        dst_file = remove_numbering(src_file) if remove_numbers else src_file
        path_dst = os.path.join(dst,dst_file)
        print(src_file,'->', dst_file)
        if os.path.isfile(path_dst):
            print('   - No copy - already exists')
        else:
            shutil.copyfile(path_src, path_dst)  

def no_ext_cmp(file, files):
    file = os.path.splitext(file)[0]
    for file2 in files:
        if file == os.path.splitext(file2)[0]: return True
    return False

def img(dir, img, romext, imgext):
    img_extensions = ['jpg', 'jpeg', 'gif', 'tiff', 'png', 'bmp']
    if img == '*' : img = dir
    rom_files = listfiles(dir, romext)
    img_files = listfiles(img, imgext)
    if romext == '*':
        rom_files = list(filter(lambda x: extension(x) not in img_extensions, rom_files))
    if imgext == '*':
        img_files = list(filter(lambda x: extension(x) in img_extensions, img_files))
    rom_img_match = list(filter(lambda x: no_ext_cmp(x, img_files), rom_files))
    rom_img_no_match = list(filter(lambda x: not no_ext_cmp(x, img_files), rom_files))
    img_rom_no_match = list(filter(lambda x: not no_ext_cmp(x, rom_files), img_files))

    print('Nbr of roms with matching image:   ', len(rom_img_match))
    print()
    print('Nbr of roms with no matching image:', len(rom_img_no_match))
    for rom in rom_img_no_match:
        print('   ', rom)
    print()
    print('Nbr of images with no matching rom:', len(img_rom_no_match))
    for img in img_rom_no_match:
        print('   ', img)


def main():
    parser = argparse.ArgumentParser(description='Emulator ROM tool')
    subparsers = parser.add_subparsers(help='Command', dest='cmd')

    copy_parser = subparsers.add_parser('copy', help='Copy files')
    copy_parser.add_argument('src', help='Source directory')
    copy_parser.add_argument('dst', help='Destination directory')
    copy_parser.add_argument('-e', '--ext', help='Extension', default='*')
    copy_parser.add_argument('-n', '--removenum', help='Remove prefix numbering', action='store_true')
    copy_parser.add_argument('-r', '--removesim', help='Remove similar files at dst', action='store_true')

    diff_parser = subparsers.add_parser('diff', help='Diff directories')
    diff_parser.add_argument('src', help='Source directory')
    diff_parser.add_argument('dst', help='Destination directory')
    diff_parser.add_argument('-e', '--ext', help='Extension', default='*')

    dup_parser = subparsers.add_parser('dup', help='Check for duplicates')
    dup_parser.add_argument('dir', help='Directory')
    dup_parser.add_argument('-e', '--ext', help='Extension', default='*')
    dup_parser.add_argument('-d', '--del', help='Delete binary identical files', action='store_true')

    img_parser = subparsers.add_parser('img', help='Check missing images')
    img_parser.add_argument('dir', help='Directory')
    img_parser.add_argument('img', help='Image directory (default same as dir)', nargs='?', default='*')
    img_parser.add_argument('-re', '--romext', help='ROM extension', default='*')
    img_parser.add_argument('-ie', '--imgext', help='Image extension', default='*')

    rep_parser = subparsers.add_parser('rep', help='Replace strings in file names')
    rep_parser.add_argument('dir', help='Directory')
    rep_parser.add_argument('org', help='From string')
    rep_parser.add_argument('new', help='To string')
    rep_parser.add_argument('-e', '--ext', help='Extension', default='*')

    zip_parser = subparsers.add_parser('zip', help='Zip all files in directory')
    zip_parser.add_argument('dir', help='Directory')
    zip_parser.add_argument('-e', '--ext', help='Extension', default='*')
    zip_parser.add_argument('-d', '--del', help='Delete file after zip', action='store_true')

    unzip_parser = subparsers.add_parser('unzip', help='Unzip all files in directory')
    unzip_parser.add_argument('dir', help='Directory')
    unzip_parser.add_argument('-d', '--del', help='Delete zip file after unzip', action='store_true')

    args = vars(parser.parse_args())

    if args['cmd'] == 'copy':
        copy(args['src'], args['dst'], args['ext'], args['removenum'], args['removesim'])
    elif args['cmd'] == 'diff': 
        diff(args['src'], args['dst'], args['ext'])
    elif args['cmd'] == 'dup': 
        dup(args['dir'], args['ext'], args['del'])     
    elif args['cmd'] == 'rep': 
        replace(args['dir'], args['org'], args['new'], args['ext'])  
    elif args['cmd'] == 'zip': 
        zip(args['dir'], args['ext'], args['del'])     
    elif args['cmd'] == 'unzip': 
        unzip(args['dir'], args['del'])   
    elif args['cmd'] == 'img': 
        img(args['dir'], args['img'], args['romext'], args['imgext'])   
    else:
        print('Invalid command:', args['cmd'])

if __name__ == '__main__':
    main()    