import pycstruct, sounddevice, argparse
import matplotlib.pyplot as plt
import numpy as np

def read_wav(filename):
    # WAV file header
    header_def = pycstruct.StructDef(default_byteorder = 'little')
    header_def.add('utf-8', 'ChunkID', length=4)
    header_def.add('uint32', 'ChunkSize')
    header_def.add('utf-8', 'Format', length=4)
    header_def.add('utf-8', 'Subchunk1ID', length=4)
    header_def.add('uint32', 'Subchunk1Size')
    header_def.add('uint16', 'AudioFormat')
    header_def.add('uint16', 'NumChannels')
    header_def.add('uint32', 'SampleRate')
    header_def.add('uint32', 'ByteRate')
    header_def.add('uint16', 'BlockAlign')
    header_def.add('uint16', 'BitsPerSample')
    header_def.add('utf-8', 'Subchunk2ID', length=4)
    header_def.add('uint32', 'Subchunk2Size')


    with open(filename, 'rb') as f:
        # Read header to figure out data size and length
        header_bytes = f.read(header_def.size())
        header = header_def.deserialize(header_bytes)
        print('WAV Header:')
        print(header)
        print()

        # Read the data
        data_def = pycstruct.StructDef(default_byteorder = 'little')
        nbr_elements = int(8 * header['Subchunk2Size'] / header['BitsPerSample'])
        data_def.add('uint' + str(header['BitsPerSample']), 'data', length=nbr_elements)
        data_bytes = f.read()
        data = data_def.deserialize(data_bytes)
        print('Number of samples:',len(data['data']))
        print()

    # Convert to numpy array
    return (np.array(data['data'], dtype=np.uint8), header['SampleRate'])

def main():
    parser = argparse.ArgumentParser(description='Play sound from a wav')
    parser.add_argument('filename', help='WAV filename')
    args = vars(parser.parse_args())

    sound, sample_rate = read_wav(args['filename'])

    # Play sound
    duration = len(sound) / sample_rate
    print(f"Playing {args['filename']} for {duration} s")
    sounddevice.play(sound, samplerate=sample_rate, blocking=True)

    # Plot audio signal
    plt.title(args['filename'])
    plt.plot(sound)
    plt.show()

    # FFT to show the frequency domain
    plt.title(f"Frequency domain")
    fft_sound = np.fft.fft(sound)
    fft_freq = np.fft.fftfreq(n=sound.size, d=1/sample_rate)
    plt.plot(fft_freq, fft_sound.real)
    print(fft_freq)
    plt.show()

if __name__ == '__main__':
    main() 










