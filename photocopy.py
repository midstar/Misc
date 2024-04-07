# -*- coding: utf-8 -*-

import argparse, os, sys, datetime, shutil



class PhotoCopy:
    month_to_path = {
        1 : '01 Januari',
        2 : '02 Februari',
        3 : '03 Mars',
        4 : '04 April',
        5 : '05 Maj',
        6 : '06 Juni',
        7 : '07 Juli',
        8 : '08 Augusti',
        9 : '09 September',
        10: '10 Oktober',
        11: '11 November',
        12: '12 December'
    }

    # Status constants
    STAT_COPY     = 'Copied'
    STAT_EXISTED  = 'Already Existed'
    STAT_FAILED   = 'Failed'
    STAT_FINISHED = 'Finished'

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

        # Stats
        self.success = []
        self.already_existed = []
        self.failed = []    
        self.last_error = None

        # Save all files to copy and figure out destination path
        self.src_paths = []
        self.dst_paths = {} # Keyed on src_path
        for root,subdirs,files in os.walk(src):
            for file in files:
                src_path = os.path.join(root,file)
                self.src_paths.append(src_path)

                # Figure out dst path
                ctime = os.path.getctime(src_path)
                cdt = datetime.datetime.fromtimestamp(ctime)
                dst_path = os.path.join(dst, str(cdt.year), self.month_to_path[cdt.month], file)
                self.dst_paths[src_path] = dst_path
        
        # Sort and set index
        self.src_paths.sort()
        self.index = 0
    
    def copy_next(self):
        if self.index >= len(self.src_paths):
            return PhotoCopy.STAT_FINISHED

        src_path = self.src_paths[self.index]
        self.index += 1
        dst_path = self.dst_paths[src_path]
        if os.path.isfile(dst_path):
            self.already_existed.append(dst_path)
            return PhotoCopy.STAT_EXISTED
        else:
            try:
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                self.success.append(dst_path)
                return PhotoCopy.STAT_COPY
            except Exception as e:
                self.failed.append(dst_path)
                self.last_error = e
                print(e)
                return PhotoCopy.STAT_FAILED
    
    # Value between 0 - 100
    def get_progress(self):
        max = len(self.src_paths)
        if max == 0:
            return 100
        return int((self.index / max) * 100.0)

class ProgressBar:
    def __init__(self, max_value = 100):
        steps = 7 * 10
        self.step_size = max_value / steps
        self.step_current = 0
        self.refresh()

    def refresh(self):
        print('|  10% |  20% |  30% |  40% |  50% |  60% |  70% |  80% |  90% | 100% |')
        print('*' + '*' * (self.step_current), end='')
        sys.stdout.flush() 
    
    def update(self, current_value):
        step_current = int(current_value / self.step_size)
        if step_current > self.step_current:
            print('*' * (step_current - self.step_current), end='')
            sys.stdout.flush() 
            self.step_current = step_current

def main():
    parser = argparse.ArgumentParser(description='Copy photo to year month structure')
    parser.add_argument('src', help='Source directory')
    parser.add_argument('dst', help='Destination directory')
    args = vars(parser.parse_args())

    pc = PhotoCopy(args['src'], args['dst'])

    # Setup progress bar
    nbr_files = len(pc.src_paths)
    #if nbr_files == 0:
    #    print('No files found to copy')
    #    exit(0)
    print('Files to copy:', nbr_files)  
    print()  
    progress_bar = ProgressBar()

    # Start copy
    while pc.copy_next() != PhotoCopy.STAT_FINISHED:
        progress_bar.update(pc.get_progress())

    # Summarize result
    print()
    print()
    print(f'{len(pc.success)} of {nbr_files} files copied')
    if (len(pc.already_existed) > 0):
        print(f'{len(pc.already_existed)} of {nbr_files} files already existed')
    if (len(pc.failed) > 0):
        print(f'{len(pc.failed)} of {nbr_files} files failed')

    full_report = input('View full report? [y/N]: ') 
    if full_report.lower() == 'y':
        print()
        print('-------------------------------------------------------------------------------')
        print('|                                FILES COPIED                                  |')
        print('-------------------------------------------------------------------------------')
        for file in sorted(pc.success):
            print(file)
        print()
        print('-------------------------------------------------------------------------------')
        print('|                           FILES ALREADY EXISTED                              |')
        print('-------------------------------------------------------------------------------')
        for file in sorted(pc.already_existed):
            print(file)
        print()
        print('-------------------------------------------------------------------------------')
        print('|                                FILES FAILED                                 |')
        print('-------------------------------------------------------------------------------')
        for file in sorted(pc.failed):
            print(file)








if __name__ == '__main__':
    main()    