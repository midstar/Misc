# -*- coding: utf-8 -*-

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

def remove_brackets(filename,start,stop):
    while start in filename and stop in filename:
        start_i = filename.index(start)
        stop_i  = filename.index(stop)
        if stop_i < start_i:
            break
        filename = filename[:start_i] + filename[stop_i + 1:]
    return filename

def remove_meta(game_name):
    for start, stop in [('(',')'),('[',']'),('<','>')]:
        game_name = remove_brackets(game_name, start, stop)

    return game_name.strip()

def main():
    parser = argparse.ArgumentParser(description='Inventory of games')
    parser.add_argument('dir', help='Root directory')
    args = vars(parser.parse_args())

    games = {}
    total = 0
    for root, _, files in os.walk(args['dir']):
        if 'Imgs/' in root:
            continue # Sort of hacky
        _, dir = os.path.split(root)
        if dir in emulators:
            for filename in files:
                if os.path.splitext(filename)[1][1:].lower() in ext:
                    total += 1
                    game_name = remove_meta(os.path.splitext(filename)[0])
                    if game_name not in games:
                        games[game_name] = set()
                    games[game_name].add(dir)
            
    used_emulators = []        
    print('----------------------------------------------------------------------------')
    print('                                  SUMMARY                                   ')
    print('----------------------------------------------------------------------------')
    print('Total number of games: ', total)
    print('Total number of titles:', len(games.keys()))
    print()
    for emulator, emulator_name in sorted(emulators.items(), key=lambda x: x[1]):
        nbr_games = 0
        for game, for_emulator in games.items():
            if emulator in for_emulator: nbr_games += 1
        if nbr_games > 0: 
            used_emulators.append(emulator)
            print(f'{emulator_name}:', nbr_games)

    print('')
    print('----------------------------------------------------------------------------')
    print('                               ALL GAMES                                    ')
    print('----------------------------------------------------------------------------')
    for game, for_emulator in sorted(games.items(), key=lambda x: x[0].lower()):
        emulator_names = []
        for emulator in for_emulator: emulator_names.append(emulators[emulator])
        emulator_names.sort()
        print(f'{game :60}  ({" / ".join(emulator_names)})')
    
    for emulator in used_emulators:
        print('')
        print('----------------------------------------------------------------------------')
        print(emulators[emulator])
        print('----------------------------------------------------------------------------')  
        for game, for_emulator in sorted(games.items(), key=lambda x: x[0].lower()):
            if emulator in for_emulator:
                print(game)

if __name__ == '__main__':
    main()    