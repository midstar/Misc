# -*- coding: utf-8 -*-

import argparse
import xml.etree.ElementTree as ET 

def main():
    parser = argparse.ArgumentParser(description='Rename files according to screenscraper.fr dat files')
    parser.add_argument('dat', help='.dat file (xml)')
    args = vars(parser.parse_args())
    
    with open(args['dat'], encoding='utf-8') as f:
        t = f.read()
       
    print(t)
    '''
    root = ET.parse(args['dat']).getroot() 

    for game in root.findall('game'):
        name = game.attrib['name'].encode('utf-8')
        print(name)
        print(name.decode('utf-8-sig'))
        #print(game.find('rom').attrib['name'])
    '''
if __name__ == '__main__':
    main()    