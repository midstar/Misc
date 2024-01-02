# This is a tool useful for handling Emulator ROM files

import argparse, os, shutil, filecmp, zipfile

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


def diff_file(src_file, dst_file, src, dst):
    
    if src_file == dst_file:
        print(src_file,'=', dst_file)
        print('   - Exact filename match')
    elif approximate_match(src_file, dst_file):
        print(src_file,'=', dst_file)
        print('   - Approximate filename match')
    else:
        return False

    src_path = os.path.join(src,src_file)
    dst_path = os.path.join(dst,dst_file)
    src_size = os.stat(src_path).st_size
    dst_size = os.stat(dst_path).st_size

    if src_size == dst_size:
        if filecmp.cmp(src_path,dst_path, shallow=False):
            print('   - File contents are identical') 
            return True
        else:
            print(f'   - Files contents are not identical but has same size ({src_size} bytes)')
    else:
        print(f'   - File size differs ({src_size} vs {dst_size} bytes)')
    return False


def diff(src, dst, ext):
    src_files = listfiles(src, ext)
    dst_files = listfiles(dst, ext)

    for src_file in src_files:
        for dst_file in dst_files:
            diff_file(src_file, dst_file, src, dst)

def dup(dir, ext, delete_identical):
    files = listfiles(dir, ext)

    while files:
        file = files.pop()
        for file2 in files:
            if diff_file(file, file2, dir, dir) and delete_identical:
                print('   - Deleting file', file)
                os.remove(os.path.join(dir,file))
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

def zip(dir, ext):
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

def copy(src, dst, ext, remove_numbers):
    print('SRC:', src)
    print('DST:', dst)
    print()
    for filename in listfiles(src, ext):
        pathname = os.path.join(src,filename)
        filename_dst = remove_numbering(filename) if remove_numbers else filename
        pathname_dst = os.path.join(dst,filename_dst)

        print(filename,'->', filename_dst)
        if os.path.isfile(pathname_dst):
            print('  No copy - already exists')
        else:
            shutil.copyfile(pathname, pathname_dst)  

def main():
    parser = argparse.ArgumentParser(description='Emulator ROM tool')
    subparsers = parser.add_subparsers(help='Command', dest='cmd')

    copy_parser = subparsers.add_parser('copy', help='Copy files')
    copy_parser.add_argument('src', help='Source directory')
    copy_parser.add_argument('dst', help='Destination directory')
    copy_parser.add_argument('-e', '--ext', help='Extension', default='*')
    copy_parser.add_argument('-n', '--remove-numbering', help='Remove prefix numbering', action='store_true')

    diff_parser = subparsers.add_parser('diff', help='Diff directories')
    diff_parser.add_argument('src', help='Source directory')
    diff_parser.add_argument('dst', help='Destination directory')
    diff_parser.add_argument('-e', '--ext', help='Extension', default='*')

    dup_parser = subparsers.add_parser('dup', help='Check for duplicates')
    dup_parser.add_argument('dir', help='Directory')
    dup_parser.add_argument('-e', '--ext', help='Extension', default='*')
    dup_parser.add_argument('-d', '--del', help='Delete binary identical files', action='store_true')

    rep_parser = subparsers.add_parser('rep', help='Replace strings in file names')
    rep_parser.add_argument('dir', help='Directory')
    rep_parser.add_argument('org', help='From string')
    rep_parser.add_argument('new', help='To string')
    rep_parser.add_argument('-e', '--ext', help='Extension', default='*')

    zip_parser = subparsers.add_parser('zip', help='Zip all files in directory')
    zip_parser.add_argument('dir', help='Directory')
    zip_parser.add_argument('-e', '--ext', help='Extension', default='*')

    args = vars(parser.parse_args())

    if args['cmd'] == 'copy':
        copy(args['src'], args['dst'], args['ext'], args['remove-numbering'])
    elif args['cmd'] == 'diff': 
        diff(args['src'], args['dst'], args['ext'])
    elif args['cmd'] == 'dup': 
        dup(args['dir'], args['ext'], args['del'])     
    elif args['cmd'] == 'rep': 
        replace(args['dir'], args['org'], args['new'], args['ext'])  
    elif args['cmd'] == 'zip': 
        zip(args['dir'], args['ext'])     
    else:
        print('Invalid command:', args['cmd'])

if __name__ == '__main__':
    main()    