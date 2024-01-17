import argparse, os

ext = ['zip', 'bin', 'chd', 'p8', 'pbp', 'bin', 'm3u']

emulators = {
    'AMIGA' : 'Amiga',
    'ARCADE' : 'Arcade',
    'ATARI' : 'Atari 2600',
    'COLECO' : 'ColecoVision',
    'COMMODORE' : 'Commendore 64',
    'CPC' : 'Amstrad CPC',
    'CPS1' : 'Capcom Play System 1',
    'CPS2' : 'Capcom Play System 2',
    'CPS3' : 'Capcom Play System 3',
    'DOS' : 'MS-DOS',
    'FAIRCHILD' : 'Fairchild Channel F',
    'FC' : 'Nintendo Entertainment System',
    'FDS' : 'Famicom Disk System',
    'FIFTYTWOHUNDRED' : 'Atari 5200',
    'GB' : 'Nintendo Game Boy',
    'GBA' : 'Nintendo Game Boy Advance',
    'GBC' : 'Nintendo Game Boy Color',
    'GG' : 'Sega Game Gear',
    'GW' : 'Game & Watch',
    'IGS' : 'IGS PolyGame Master',
    'INTELLIVISION' : 'Mattel Intellivision',
    'LYNX' : 'Atari Lynx',
    'MD' : 'Sega Mega Drive (Genesis)',
    'MEGADUCK' : 'Mega Duck',
    'MS' : 'Sega Master System',
    'MSX' : 'MSX - MSX2',
    'NEOCD' : 'SNK NeoGeo CD',
    'NEOGEO' : 'SNK NeoGeo',
    'NGP' : 'SNK NeoGeo Pocket & Color',
    'ODYSSEY' : 'Magnavox Odyssey 2',
    'PCE' : 'NEC TurboGrafx-16',
    'PCECD' : 'NEC TurboGrafx CD',
    'PICO' : 'PICO-8',
    'POKE' : 'Nintendo Pokemini',
    'PS' : 'Sony Playstation',
    'SATELLAVIEW' : 'Nintendo Satellaview',
    'SEGACD' : 'Sega CD',
    'SEGASGONE' : 'Sega SG-1000',
    'SEVENTYEIGHTHUNDRED' : 'Atari 7800',
    'SFC' : 'Nintendo Super Nintendo',
    'SGB' : 'Nintendo Super Game Boy',
    'SGFX' : 'NEC SuperGrafx',
    'SUFAMI' : 'Bandai Sufami Turbo',
    'SUPERVISION' : 'Watara Supervision',
    'THIRTYTWOX' : 'Sega 32X',
    'TIC' : 'TIC-80',
    'VB' : 'Nintendo Virtual Boy',
    'VECTREX' : 'GCE Vectrex',
    'VIDEOPAC' : 'VideoPac',
    'WS' : 'Bandai WonderSwan & Color'
}

def main():
    parser = argparse.ArgumentParser(description='Inventory of games')
    parser.add_argument('dir', help='Root directory')
    args = vars(parser.parse_args())

    games = {}
    
    for root, _, files in os.walk(args['dir']):
        if 'Imgs/' in root:
            continue # Sort of hacky
        _, dir = os.path.split(root)
        if dir in emulators:
            for filename in files:
                if os.path.splitext(filename)[1][1:].lower() in ext:
                    game_name = os.path.splitext(filename)[0]
                    if game_name not in games:
                        games[game_name] = set()
                    games[game_name].add(dir)
                else:
                    print('Ignoring file', filename)
            

if __name__ == '__main__':
    main()    