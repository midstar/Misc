# -*- coding: utf-8 -*-

import argparse, os, sys, datetime, shutil

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

class progressBar:
    def __init__(self, max_value):
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

    # Save all files to copy
    src_paths = []
    for root,subdirs,files in os.walk(args['src']):
        for file in files:
            src_paths.append(os.path.join(root,file))

    # Setup progress bar
    nbr_files = len(src_paths)
    if nbr_files == 0:
        print('No files found to copy')
        exit(0)
    print('Files to copy:', nbr_files)  
    print()  
    progress_bar = progressBar(nbr_files)

    # Some stats
    success = []
    already_existed = []
    failed = []

    # Start copy
    for idx, src_path in enumerate(src_paths):
        ctime = os.path.getctime(src_path)
        cdt = datetime.datetime.fromtimestamp(ctime)
        src_file = os.path.split(src_path)[1]

        dst_path = os.path.join(args['dst'], str(cdt.year), month_to_path[cdt.month], src_file)
        if os.path.isfile(dst_path):
            already_existed.append(dst_path)
        else:
            try:
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                success.append(dst_path)
            except Exception as e:
                failed.append(dst_path)

        progress_bar.update(idx + 1)

    # Summarize result
    print()
    print()
    print(f'{len(success)} of {nbr_files} files copied')
    if (len(already_existed) > 0):
        print(f'{len(already_existed)} of {nbr_files} files already existed')
    if (len(failed) > 0):
        print(f'{len(failed)} of {nbr_files} files failed')

    full_report = input('View full report? [y/N]: ') 
    if full_report.lower() == 'y':
        print()
        print('-------------------------------------------------------------------------------')
        print('|                                FILES COPIED                                  |')
        print('-------------------------------------------------------------------------------')
        for file in sorted(success):
            print(file)
        print()
        print('-------------------------------------------------------------------------------')
        print('|                           FILES ALREADY EXISTED                              |')
        print('-------------------------------------------------------------------------------')
        for file in sorted(already_existed):
            print(file)
        print()
        print('-------------------------------------------------------------------------------')
        print('|                                FILES FAILED                                 |')
        print('-------------------------------------------------------------------------------')
        for file in sorted(failed):
            print(file)








if __name__ == '__main__':
    main()    