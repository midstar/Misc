import sounddevice, argparse
import matplotlib.pyplot as plt
import numpy as np

def signal(frequency, sample_rate, duration):
    x = np.linspace(-np.pi, np.pi, sample_rate)
    signal_1sec = 127*np.sin(x * frequency)+127
    signal_1sec = signal_1sec.astype(np.uint8)
    return np.tile(signal_1sec, duration)

def main():
    parser = argparse.ArgumentParser(description='Play sound from a sine wave')
    parser.add_argument('frequency', help='Frequency in Hz', type=int)
    parser.add_argument('duration', help='Duration in sec (default 5 sec)', default=5, nargs='?', type=int)
    parser.add_argument('sample_rate', help='Samples per sec (default 48000 Hz)', default=48000, nargs='?', type=int)
    args = vars(parser.parse_args())

    sound = signal(args['frequency'], args['sample_rate'], args['duration'])
    print(f"Playing {args['frequency']} Hz for {args['duration']} s")
    sounddevice.play(sound, samplerate=args['sample_rate'], blocking=True)

    plt.title(f"{args['frequency']} Hz during 1 s using {args['sample_rate']} samples / s")
    plt.plot(sound[:args['sample_rate']])
    plt.show()

    

        

if __name__ == '__main__':
    main() 









