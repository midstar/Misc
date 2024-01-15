# This is a tool useful for handling Emulator ROM files

import argparse, os, shutil, filecmp, zipfile, tempfile

TEMPDIR = os.path.join(tempfile.gettempdir(), 'romtool')

def remove_numbering(filename):
    if ' ' in filename and filename[:filename.index(' ')].isnumeric():
        filename = filename[filename.index(' ') + 1:] 
    return filename

def no_ext(filename):
    return os.path.splitext(filename)[0]

def get_ext(filename):
    return os.path.splitext(filename)[-1][1:].lower()

def listfiles(path, ext):
    filenames = []
    for filename in os.listdir(path):  
        pathname = os.path.join(path,filename)
        if not os.path.isfile(pathname): continue
        if ext.lower() not in ['*', get_ext(filename)]: continue
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

def remove_meta(filename):
    filename = no_ext(filename)

    filename = remove_numbering(filename).lower()

    for start, stop in [('(',')'),('[',']'),('<','>')]:
        filename = remove_brackets(filename, start, stop)

    return filename

def fix_filename(filename):
    filename = remove_meta(filename)

    for c in '!@#$%^&*()[]{};:,./<>?\|"\'`~-=_+ ':
        filename = filename.replace(c,'')

    return filename

def get_words(filename):
    filename = remove_meta(filename)
    for c in '!@#$%^&*()[]{};:,./<>?\|"\'`~-=_+ ':
        filename = filename.replace(c,' ')
    return filename.split()

def get_version(filename):
    filename2 = get_words(filename)
    filename2 = filename2[1:] # Version is never first

    for v in range(10,0,-1):
        if str(v) in filename2:
            filename = filename.replace(str(v), '')
            return (filename, v)

    for i, v in enumerate(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']):
        if v in filename2:
            filename = filename.replace(v, '')
            return (filename, i+1)
    
    return (filename, 1)

def score_match(src_file, dst_file):
    src_words = get_words(src_file)
    dst_words = get_words(dst_file)
    if len(src_words) < len(dst_words):
        words1 = src_words
        words2 = dst_words
    else:
        words1 = dst_words
        words2 = src_words

    matches = 0
    for w in words1:
        if w in words2: matches += 1
    return matches / len(words1)


def approximate_match(src_file, dst_file):
    src_file, src_version = get_version(src_file)
    dst_file, dst_version = get_version(dst_file)

    src_file_f = fix_filename(src_file)
    dst_file_f = fix_filename(dst_file)
    if (src_file_f in dst_file_f or dst_file_f in src_file_f) and src_version == dst_version:
        return True
    if score_match(src_file, dst_file) > 0.6 and src_version == dst_version:
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
    
    if get_ext(src_file) == 'zip' or get_ext(dst_file) == 'zip':
        if get_ext(src_file) == 'zip':
            src_path, src_size = extract_zip(src_path, 'src')
        if get_ext(dst_file) == 'zip':
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

def dup(dir, ext, delete_similar, same_content):
    files = listfiles(dir, ext)

    while files:
        file = files.pop(0)
        for file2 in files:
            diff_res = diff_file(file, file2, dir, dir)
            if diff_res[0] and (same_content == False or diff_res[4]):
                print_diff(*diff_res)
                if delete_similar:
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

def rename(dir, names_file, ext):
    files = listfiles(dir, ext)
    with open(names_file, 'r') as f:
        names = f.read().splitlines()
    
    for filename in files:
        if no_ext(filename) in names:
            print('No change:',filename)
            continue
        else:
            matches = []
            for name in names:
                name_w_ext = name + '.' + get_ext(filename)
                if approximate_match(filename, name_w_ext):
                    matches.append(name_w_ext)
            if len(matches) == 0:     
                print('Unable to match:',filename)
                filename_new = input(f'Enter filename. [blank for no action, x=delete]:')
            else:
                print('Suggested:',filename)
                for i, match in enumerate(matches):
                    print(f'[{i + 1}]   {match}')
                filename_new = input(f'Select option, enter filename [blank for no action, x=delete]:')
                print(filename_new)
                if filename_new.isnumeric() and int(filename_new) < (len(matches) + 1):
                    filename_new = matches[int(filename_new) - 1]
            if filename_new == 'x':
                print('Deleted', filename)
                os.remove(os.path.join(dir,filename))
            elif filename_new != '':
                if get_ext(filename_new).lower() != get_ext(filename).lower():
                    print(filename_new, 'is not a valid filename')
                else:
                    pathname = os.path.join(dir,filename)
                    pathname_new = os.path.join(dir,filename_new)
                    print(filename,'->', filename_new)
                    os.rename(pathname, pathname_new)
        print()

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
        if get_ext(filename) != 'zip':
            zip_filename = no_ext(filename) + '.zip'
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

def img(dir, img, romext, imgext, summary, movedir):
    img_extensions = ['jpg', 'jpeg', 'gif', 'tiff', 'png', 'bmp']
    if img == '*' : img = dir
    rom_files = listfiles(dir, romext)
    img_files = listfiles(img, imgext)

    if romext == '*':
        rom_files = list(filter(lambda x: get_ext(x) not in img_extensions, rom_files))
    if imgext == '*':
        img_files = list(filter(lambda x: get_ext(x) in img_extensions, img_files))
    rom_img_match = list(filter(lambda x: no_ext_cmp(x, img_files), rom_files))
    rom_img_no_match = list(filter(lambda x: not no_ext_cmp(x, img_files), rom_files))
    img_rom_no_match = list(filter(lambda x: not no_ext_cmp(x, rom_files), img_files))


    print('Nbr of roms with matching image:   ', len(rom_img_match))
    print()
    print('Nbr of roms with no matching image:', len(rom_img_no_match))
    if not summary:
        for rom in rom_img_no_match: print(rom)
    print()
    print('Nbr of images with no matching rom:', len(img_rom_no_match))
    if not summary:
        for img in img_rom_no_match: print(img)
    
    if movedir != '':
        if not os.path.exists(movedir):
            print(f'Error! Path "{movedir}" do not exist')
        else:
            for rom in rom_img_no_match: 
                path_src = os.path.join(dir,rom)
                path_dst = os.path.join(movedir,rom)
                print('->',path_dst)
                shutil.move(path_src,path_dst)


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
    dup_parser.add_argument('-d', '--del', help='Delete similar files (ask first)', action='store_true')
    dup_parser.add_argument('-i', '--identical', help='Only list files with same content', action='store_true')

    img_parser = subparsers.add_parser('img', help='Check missing images')
    img_parser.add_argument('dir', help='Directory')
    img_parser.add_argument('img', help='Image directory (default same as dir)', nargs='?', default='*')
    img_parser.add_argument('-re', '--romext', help='ROM extension', default='*')
    img_parser.add_argument('-ie', '--imgext', help='Image extension', default='*')
    img_parser.add_argument('-s', '--summary', help='Print summary only', action='store_true')
    img_parser.add_argument('-md', '--movedir', help='Move roms with no image to directory',default='')

    rep_parser = subparsers.add_parser('rep', help='Replace strings in file names')
    rep_parser.add_argument('dir', help='Directory')
    rep_parser.add_argument('org', help='From string')
    rep_parser.add_argument('new', help='To string')
    rep_parser.add_argument('-e', '--ext', help='Extension', default='*')

    rename_parser = subparsers.add_parser('rename', help='Rename files base on allwed names')
    rename_parser.add_argument('dir', help='Directory')
    rename_parser.add_argument('names', help='Text file with allowed names separated with new line')
    rename_parser.add_argument('-e', '--ext', help='Extension', default='*')

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
        dup(args['dir'], args['ext'], args['del'], args['identical'])   
    elif args['cmd'] == 'rep': 
        replace(args['dir'], args['org'], args['new'], args['ext']) 
    elif args['cmd'] == 'rename': 
        rename(args['dir'], args['names'], args['ext'])    
    elif args['cmd'] == 'zip': 
        zip(args['dir'], args['ext'], args['del'])     
    elif args['cmd'] == 'unzip': 
        unzip(args['dir'], args['del'])   
    elif args['cmd'] == 'img': 
        img(args['dir'], args['img'], args['romext'], args['imgext'], args['summary'], args['movedir'])   
    else:
        print('Invalid command:', args['cmd'])

if __name__ == '__main__':
    main()    