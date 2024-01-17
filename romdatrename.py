# -*- coding: utf-8 -*-

import argparse, os
import xml.etree.ElementTree as ET 

def main():
    parser = argparse.ArgumentParser(description='Rename files according to screenscraper.fr dat files')
    parser.add_argument('dat', help='.dat file (xml)')
    parser.add_argument('-e', '--ext', help='File extension', default='*')
    args = vars(parser.parse_args())
    
    root = ET.parse(args['dat']).getroot() 

    for game in root.findall('game'):
        name = game.attrib['name']
        filename = game.find('rom').attrib['name']
        fname, fext = os.path.splitext(filename)
        if args['ext'] != '*':
            fext = '.' + args['ext']
        from_filename = fname + fext
        to_filename = name + fext
        print(from_filename, ' -> ', to_filename)
        try:
            os.rename(from_filename, to_filename)
        except Exception as e:
            print(e)

        

if __name__ == '__main__':
    main()    